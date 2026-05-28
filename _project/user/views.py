from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum, Q, F, DecimalField, ExpressionWrapper
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from decimal import Decimal
from datetime import date

from .models import RecentAction, Client, Sale, Payment, Kind, Item, Lose, Daycome, Safe, Supplier


# ─── Helpers ────────────────────────────────────────────────────────────────

def paginate(queryset, page, per_page=20):
    """Return a paginated page object from a queryset."""
    paginator = Paginator(queryset, per_page)
    try:
        return paginator.page(page)
    except PageNotAnInteger:
        return paginator.page(1)
    except EmptyPage:
        return paginator.page(paginator.num_pages)


def log_action(request, action_type, action_sort, model_affected):
    """Create a RecentAction audit log entry."""
    RecentAction.objects.create(
        user=request.user if request.user.is_authenticated else None,
        action_type=action_type,
        action_sort=action_sort,
        model_affected=model_affected,
    )


def restore_item_quantity(sale):
    """Restore item stock when a sale is deleted."""
    Item.objects.filter(id=sale.item.id).update(
        quantity=F('quantity') + sale.sale_quantity
    )


# ─── Auth ────────────────────────────────────────────────────────────────────

def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        messages.warning(request, 'كلمة المرور غير صحيحة')
    return render(request, 'login.html')


def logout_user(request):
    logout(request)
    return render(request, 'logout.html')


# ─── Home ────────────────────────────────────────────────────────────────────

@login_required(login_url="login")
def home(request):
    shorts_number = Item.objects.filter(quantity=0).count()
    context = {
        "clients_number": Client.objects.count(),
        "items_number": Item.objects.count(),
        "suppliers_number": Supplier.objects.count(),
        "shorts_number": shorts_number,
    }
    return render(request, "home.html", context)


# ─── Kinds ───────────────────────────────────────────────────────────────────

def kinds(request):
    if "addKind" in request.POST:
        Kind.objects.create(name=request.POST.get('name'))
        messages.success(request, "تم اضافة نوع بنجاح")
        return redirect("kinds")

    context = {'kinds': Kind.objects.all()}
    return render(request, "kinds.html", context)


def kind_delete(request, id):
    kind = get_object_or_404(Kind, id=id)
    if "kindDelete" in request.POST:
        kind.delete()
        messages.success(request, "تم حذف النوع بنجاح")
        return redirect("kinds")


# ─── Items ───────────────────────────────────────────────────────────────────

def items(request):
    all_items = Item.objects.all().order_by("-date")
    page = request.GET.get('page')
    item_list = paginate(all_items, page, per_page=20)

    if "addItem" in request.POST:
        return _handle_add_item(request)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        item_list = list(Item.objects.filter(Q(name__icontains=search_input)))

    context = {'items': item_list, 'kinds': Kind.objects.all()}
    return render(request, "items.html", context)


def _handle_add_item(request):
    name = request.POST.get('name')
    kind_name = request.POST.get('kind')
    prand = request.POST.get('prand')
    quantity = request.POST.get('quantity')
    price = request.POST.get('price')
    item_date = request.POST.get('date') or date.today()
    item_id = request.POST.get('item_id')

    if Item.objects.filter(name=name).exclude(id=item_id).exists():
        messages.warning(request, f'المنتج ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect("items")

    kind = Kind.objects.get(name=kind_name)
    Item.objects.create(name=name, kind=kind, prand=prand, quantity=quantity, price=price, date=item_date)
    messages.success(request, "تم اضافة صنف بنجاح")
    return redirect("items")


def item_delete(request, id):
    item = get_object_or_404(Item, id=id)
    if "itemDelete" in request.POST:
        item.delete()
        messages.success(request, "تم حذف المنتج بنجاح")
        return redirect("items")


def _apply_item_update(request, id, redirect_target):
    """Shared logic for updating an item from either items or shorts page."""
    name = request.POST['name']
    kind_name = request.POST['kind_name']
    prand = request.POST['prand']
    quantity = request.POST['quantity']

    if Item.objects.filter(name=name).exclude(id=id).exists():
        messages.warning(request, f'المنتج ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect(redirect_target)

    kind = Kind.objects.get(name=kind_name)
    item = Item.objects.get(id=id)
    item.name = name
    item.kind = kind
    item.prand = prand
    item.quantity = quantity
    item.save()

    messages.success(request, 'تم تعديل بيانات الصنف بنجاح', extra_tags='success')
    return redirect(redirect_target)


def item_update(request, id):
    if 'itemUpdate' in request.POST:
        return _apply_item_update(request, id, "items")
    if 'itemUpdateShort' in request.POST:
        return _apply_item_update(request, id, "shorts")


# ─── Sales ───────────────────────────────────────────────────────────────────

def sale_page(request):
    all_items = Item.objects.all().order_by("-date")
    page = request.GET.get('page')
    items_list = paginate(all_items, page, per_page=20)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        items_list = list(Item.objects.filter(Q(name__icontains=search_input)))

    return render(request, "sales.html", {"items": items_list})


@login_required(login_url="login")
def sell(request, id):
    if "sell" not in request.POST:
        return redirect("sales")

    item = get_object_or_404(Item, pk=request.POST.get('item'))
    data = _extract_sale_form_data(request)

    if data['sale_quantity'] > item.quantity:
        messages.error(request, "الكمية المباعة اكبر من الكمية المتبقية")
        return redirect("sales")

    client_name = data['client_name']
    client = None

    if client_name and client_name != "-":
        client = _get_or_create_client(client_name)

    Sale.objects.create(
        client=client,
        item=item,
        date=data['sale_date'],
        crash=data['crash'],
        sale_price=data['sale_price'],
        remain=data['remain'],
        paid=data['paid'],
        sale_quantity=data['sale_quantity'],
        client_phone=data['client_phone'],
        method=data['method'],
        client_name=client_name,
    )
    Item.objects.filter(id=item.id).update(quantity=F('quantity') - data['sale_quantity'])

    messages.success(request, "تمت إضافة عملية بيع بنجاح")
    return redirect("sales")


def _extract_sale_form_data(request):
    """Parse and normalise sale form POST data."""
    client_name = (request.POST.get('client_name') or '').strip() or "-"
    client_phone = request.POST.get('client_phone') or "-"
    crash = request.POST.get('crash') or "-"
    sale_date = request.POST.get('date') or date.today()
    method = request.POST.get('method')
    sale_price = Decimal(request.POST.get('sale_price'))
    sale_quantity = Decimal(request.POST.get('sale_quantity'))
    paid = Decimal(request.POST.get('paid') or 0)
    remain = Decimal(request.POST.get('remain'))

    return {
        'client_name': client_name,
        'client_phone': client_phone,
        'crash': crash,
        'sale_date': sale_date,
        'method': method,
        'sale_price': sale_price,
        'sale_quantity': sale_quantity,
        'paid': paid,
        'remain': remain,
    }


def _get_or_create_client(name):
    client, _ = Client.objects.get_or_create(
        name=name,
        defaults={'phone': "-", 'opening_balance': 0, 'notes': "-"}
    )
    return client


def _apply_sale_update(request, id):
    """Update shared sale fields (client_name, paid, method)."""
    sale = Sale.objects.get(id=id)
    sale.client_name = request.POST["client_name"]
    sale.paid = request.POST["paid"]
    sale.method = request.POST["method"]
    sale.save()
    messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')


def sale_update(request, id):
    if "saleUpdate" in request.POST:
        _apply_sale_update(request, id)
        return redirect("profits")

    if "saleUpdate2" in request.POST:
        _apply_sale_update(request, id)
        return redirect("tempsales")

    if "saleUpdate3" in request.POST:
        client_id = get_object_or_404(Sale, id=id).client.id
        _apply_sale_update(request, id)
        return redirect("clientpage", id=client_id)


def _restore_and_delete_sale(sale):
    restore_item_quantity(sale)
    sale.delete()
    messages.success


def sale_delete(request, id):
    sale = get_object_or_404(Sale, id=id)

    if "saleDelete" in request.POST:
        restore_item_quantity(sale)
        sale.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")

    if "saleDelete2" in request.POST:
        restore_item_quantity(sale)
        sale.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("tempsales")

    if "saleDelete3" in request.POST:
        client_id = sale.client.id
        restore_item_quantity(sale)
        sale.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("clientpage", id=client_id)


def paid_done(request, id):
    sale = get_object_or_404(Sale, id=id)
    if "paidDone" in request.POST:
        sale.paid = sale.total
        sale.remain = 0
        sale.save()
        messages.success(request, "تم تأكيد الدفع بنجاح")
        return redirect("tempsales")


# ─── Clients ─────────────────────────────────────────────────────────────────

@login_required(login_url="login")
def clients(request):
    page = request.GET.get('page')
    client_list = paginate(Client.objects.all(), page, per_page=20)

    if "addClient" in request.POST:
        return _handle_add_client(request)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        client_list = list(Client.objects.filter(Q(name__icontains=search_input)))

    return render(request, "clients.html", {"clients": client_list})


def _handle_add_client(request):
    name = request.POST.get("name")
    opening_balance = request.POST.get("opening_balance") or 0
    phone = request.POST.get("phone")

    if Client.objects.filter(name=name).exists():
        messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect("clients")

    Client.objects.create(name=name, opening_balance=opening_balance, phone=phone)
    messages.success(request, "تم اضافة عميل جديد بنجاح")
    return redirect("clients")


def client_update(request, id):
    if 'clientUpdate' not in request.POST:
        return

    name = request.POST['name'].strip()
    if Client.objects.filter(name=name).exclude(id=id).exists():
        messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect("clientpage", id=id)

    client = Client.objects.get(id=id)
    client.name = name
    client.opening_balance = request.POST['opening_balance']
    client.phone = request.POST['phone']
    client.save()

    messages.success(request, 'تم تعديل بيانات العميل بنجاح', extra_tags='success')
    return redirect("clients")


def client_delete(request, id):
    client = get_object_or_404(Client, id=id)
    if "clientDelete" in request.POST:
        log_action(request, 'حذف عميل', 'حذف', f'تم حذف العميل ({client.name})')
        client.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("clients")


@login_required(login_url="login")
def client_page(request, id):
    client = get_object_or_404(Client, id=id)
    context = {
        "client": client,
        "sales": Sale.objects.filter(client=client).order_by("-date"),
        "items": Item.objects.all(),
    }
    return render(request, "clientpage.html", context)


# ─── Profits ─────────────────────────────────────────────────────────────────

@login_required(login_url="login")
def profits(request):
    page = request.GET.get('page')
    sale_list = paginate(Sale.objects.all().order_by("-date"), page, per_page=20)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        sale_list = list(Sale.objects.filter(Q(client_name__icontains=search_input)))

    return render(request, "profits.html", {"sales": sale_list})


# ─── Payments ────────────────────────────────────────────────────────────────

def pay_update(request, id):
    if "payupdate" not in request.POST:
        return

    old_data = Payment.objects.values().get(id=id)
    client_name = request.POST["client"].strip()
    paid_money = Decimal(request.POST["paid_money"])

    try:
        client_obj = Client.objects.get(name=client_name)
    except Client.DoesNotExist:
        messages.warning(request, f"اسم العميل ({client_name}) غير موجود")
        return redirect("profits")

    payment = Payment.objects.get(id=id)
    changes = _build_payment_changes(old_data, client_obj, paid_money)

    payment.client = client_obj
    payment.paid_money = paid_money
    payment.save()

    log_action(request, 'تعديل استلام نقدية', 'تعديل',
               f'تم تعديل عملية استلام نقدية: {", ".join(changes)}')
    messages.success(request, 'تم تعديل بيانات التحصيل بنجاح', extra_tags='success')
    return redirect("profits")


def _build_payment_changes(old_data, new_client, new_paid_money):
    changes = []
    if new_client.id != old_data["client_id"]:
        old_name = Client.objects.get(id=old_data["client_id"]).name
        changes.append(f'اسم العميل من {old_name} إلى {new_client.name}')
    if str(new_paid_money) != str(old_data["paid_money"]):
        changes.append(f'السعر من {old_data["paid_money"]} إلى {new_paid_money}')
    return changes


def pay_delete(request, id):
    payment = get_object_or_404(Payment, id=id)
    if "paydelete" in request.POST:
        log_action(
            request, 'حذف عملية دفع', 'حذف',
            f'تم حذف عملية دفع للعميل ({payment.client.name}) و كانت بقيمة ({payment.paid_money})'
        )
        payment.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")


# ─── Loses ───────────────────────────────────────────────────────────────────

def loses(request):
    page = request.GET.get('page')
    loses_list = paginate(Lose.objects.all().order_by("-date"), page, per_page=20)

    if "addLose" in request.POST:
        return _handle_add_lose(request)

    return render(request, 'loses.html', {'loses': loses_list})


def _handle_add_lose(request):
    notes = request.POST.get('notes') or "-"
    lose_date = request.POST.get('date') or date.today()
    Lose.objects.create(
        lose_type=request.POST.get('lose_type'),
        lose_money=request.POST.get('lose_money'),
        date=lose_date,
        notes=notes,
    )
    messages.success(request, "تم اضافة مصروف بنجاح")
    return redirect("loses")


def lose_delete(request, id):
    lose = get_object_or_404(Lose, id=id)
    if "loseDelete" in request.POST:
        lose.delete()
        messages.success(request, "تم حذف المصروف بنجاح")
        return redirect("loses")


def lose_update(request, id):
    if 'loseUpdate' not in request.POST:
        return

    lose = Lose.objects.get(id=id)
    lose.lose_type = request.POST['lose_type']
    lose.lose_money = request.POST['lose_money']
    lose.notes = request.POST['notes']
    lose.save()

    messages.success(request, 'تم تعديل بيانات المصروف بنجاح', extra_tags='success')
    return redirect("loses")


# ─── Shorts ──────────────────────────────────────────────────────────────────

def shorts(request):
    out_of_stock = Item.objects.filter(quantity=0).order_by("-date")
    page = request.GET.get('page')
    shorts_list = paginate(out_of_stock, page, per_page=30)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        shorts_list = list(Item.objects.filter(Q(name__icontains=search_input)))

    return render(request, 'shorts.html', {'items': shorts_list})


# ─── Temp Sales ──────────────────────────────────────────────────────────────

def tempsales(request):
    pending = Sale.objects.filter(remain__gt=0).order_by("-date")
    page = request.GET.get('page')
    temp_list = paginate(pending, page, per_page=30)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        temp_list = list(Sale.objects.filter(Q(client_name__icontains=search_input)))

    return render(request, 'tempsales.html', {'sales': temp_list})


# ─── Daycome ─────────────────────────────────────────────────────────────────

def daycome(request):
    safe = get_object_or_404(Safe, id=1)
    today = date.today()

    today_profits_qs = Sale.objects.filter(date=today)
    today_loses_qs = Lose.objects.filter(date=today)

    total_profits = today_profits_qs.aggregate(Sum('paid'))['paid__sum'] or 0
    total_loses = today_loses_qs.aggregate(Sum('lose_money'))['lose_money__sum'] or 0
    net_profit = total_profits - total_loses
    total_win = (
        Sale.objects.filter(date=today)
        .annotate(win=ExpressionWrapper(F('sale_price') - F('item__price'), output_field=DecimalField()))
        .aggregate(Sum('win'))['win__sum'] or 0
    )

    page = request.GET.get('page')
    comes_list = paginate(Daycome.objects.all().order_by("-date"), page, per_page=30)

    if "dayCome" in request.POST:
        return _handle_daycome_create(request)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        comes_list = list(Daycome.objects.filter(Q(date__icontains=search_input)))

    context = {
        'total_profits': total_profits,
        'total_loses': total_loses,
        'net_profit': net_profit,
        'total_win': total_win,
        'today': today,
        'daycomes': comes_list,
        'today_profits': today_profits_qs,
        'today_loses': today_loses_qs,
        'safe': safe,
    }
    return render(request, 'daycome.html', context)


def _handle_daycome_create(request):
    date_str = request.POST.get('date')
    if Daycome.objects.filter(date=date_str).exists():
        messages.warning(request, 'تقفيل هذا اليوم محفوظ بالفعل في قاعدة البيانات')
        return redirect('daycome')

    Daycome.objects.create(
        loses=request.POST.get('total_loses'),
        income=request.POST.get('total_profits'),
        date=date_str,
        net_profit=request.POST.get('net_profit'),
        win=request.POST.get('win'),
        cash=request.POST.get('cash'),
        wallet=request.POST.get('wallet'),
        payments=request.POST.get('payments'),
    )
    messages.success(request, "تم حفظ تقفيل اليوم")
    return redirect("daycome")


def daycome_delete(request, id):
    daycome = get_object_or_404(Daycome, id=id)
    if "daycomeDelete" in request.POST:
        daycome.delete()
        messages.success(request, "تم حذف التقفيل بنجاح")
        return redirect("daycome")


def daycome_update(request, id):
    if 'daycomeUpdate' not in request.POST:
        return

    dc = Daycome.objects.get(id=id)
    dc.income = request.POST['total_profits']
    dc.loses = request.POST['total_loses']
    dc.net_profit = request.POST['net_profit']
    dc.win = request.POST['win']
    dc.cash = request.POST['cash']
    dc.wallet = request.POST['wallet']
    dc.date = request.POST['date']
    dc.save()

    messages.success(request, 'تم تعديل بيانات التقفيل بنجاح', extra_tags='success')
    return redirect("daycome")


# ─── Safe ────────────────────────────────────────────────────────────────────

def safe(request):
    safe_instance = get_object_or_404(Safe, id=1)
    today = timezone.now().date()

    cash_month = Sale.objects.filter(date__date=today, method="نقدية").aggregate(Sum('paid'))['paid__sum'] or 0
    wallet_month = Sale.objects.filter(date__date=today, method="محفظة").aggregate(Sum('paid'))['paid__sum'] or 0

    if request.method == 'POST':
        if 'deposit' in request.POST:
            amount = Decimal(request.POST.get('amount'))
            kind = request.POST.get('kind')
            if kind == 'درج':
                safe_instance.cash += amount
            elif kind == 'محفظة':
                safe_instance.wallet += amount
            safe_instance.save()
            messages.success(request, "تم الايداع بنجاح")
            return redirect('safe')

        if 'cashToWallet' in request.POST:
            return _transfer_safe(request, safe_instance, from_field='cash', to_field='wallet', key='ctw')

        if 'walletToCash' in request.POST:
            return _transfer_safe(request, safe_instance, from_field='wallet', to_field='cash', key='wtc')

    context = {"safe": safe_instance, "cash_month": cash_month, "wallet_month": wallet_month}
    return render(request, "safe.html", context)


def _transfer_safe(request, safe_instance, from_field, to_field, key):
    amount = Decimal(request.POST.get(key))
    source_balance = getattr(safe_instance, from_field)
    if source_balance >= amount:
        setattr(safe_instance, from_field, source_balance - amount)
        setattr(safe_instance, to_field, getattr(safe_instance, to_field) + amount)
        safe_instance.save()
        messages.success(request, "تم الترحيل بنجاح")
    else:
        messages.error(request, "الرصيد الحالي غير كافي لهذه العملية")
    return redirect('safe')


def safe_update(request, id):
    safe_instance = Safe.objects.get(id=id)

    if 'cashUpdate' in request.POST:
        safe_instance.cash = request.POST['cash']
        safe_instance.save()
        messages.success(request, 'تم تعديل رصيد الدرج', extra_tags='success')
        return redirect("safe")

    if 'walletUpdate' in request.POST:
        safe_instance.wallet = request.POST['wallet']
        safe_instance.save()
        messages.success(request, 'تم تعديل رصيد المحفظة', extra_tags='success')
        return redirect("safe")


# ─── Suppliers ───────────────────────────────────────────────────────────────

@login_required(login_url="login")
def suppliers(request):
    page = request.GET.get('page')
    supplier_list = paginate(Supplier.objects.all(), page, per_page=30)

    if "addSupplier" in request.POST:
        return _handle_add_supplier(request)

    if 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        supplier_list = list(Supplier.objects.filter(Q(name__icontains=search_input)))

    return render(request, "suppliers.html", {'suppliers': supplier_list})


def _handle_add_supplier(request):
    name = request.POST.get('name')
    if Supplier.objects.filter(name=name).exists():
        messages.warning(request, f'اسم ألمورد ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect("suppliers")

    Supplier.objects.create(
        name=name,
        for_him=request.POST.get('for_him'),
        phone=request.POST.get('phone'),
    )
    messages.success(request, "تم اضافة مورد بنجاح")
    return redirect("suppliers")


def supplier_update(request, id):
    if 'supplierUpdate' not in request.POST:
        return

    name = request.POST['name'].strip()
    if Supplier.objects.filter(name=name).exclude(id=id).exists():
        messages.warning(request, f'اسم المورد ({name}) موجود بالفعل في قاعدة البيانات')
        return redirect("suppliers")

    supplier = Supplier.objects.get(id=id)
    supplier.name = name
    supplier.for_him = request.POST['for_him']
    supplier.phone = request.POST['phone']
    supplier.save()

    messages.success(request, 'تم تعديل بيانات المورد بنجاح', extra_tags='success')
    return redirect("suppliers")


def supplier_pay(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if "supplierPaid" in request.POST:
        supplier.for_him -= Decimal(request.POST.get("paid"))
        supplier.save()
        messages.success(request, 'تم السداد للمورد بنجاح', extra_tags='success')
        return redirect("suppliers")


def supplier_delete(request, id):
    supplier = get_object_or_404(Supplier, id=id)
    if "supplierDelete" in request.POST:
        supplier.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("suppliers")


def supplier_page(request, id):
    pass