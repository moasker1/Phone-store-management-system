from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Sum
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import RecentAction , Client , Sale , Payment, Kind, Item, Lose, Daycome, Safe, Supplier
from datetime import date
from decimal import Decimal
from django.db.models import F , DecimalField, ExpressionWrapper
#====================================================================================================================
def login_user(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username = username, password = password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.warning(request, 'كلمة المرور غير صحيحة')

    return render(request, 'login.html')
#====================================================================================================================
def logout_user(request):
    logout(request)
    return render(request, 'logout.html')
#====================================================================================================================
@login_required(login_url="login")
def home(request) :
    return render(request, "home.html")
#====================================================================================================================
def kinds(request):
    kinds = Kind.objects.all()
    if "addKind" in request.POST :
        name = request.POST.get('name')
        Kind.objects.create(name=name)
        messages.success(request,"تم اضافة نوع بنجاح")
        return redirect("kinds")
    context ={'kinds': kinds}
    return render(request, "kinds.html", context)
#====================================================================================================================
def kind_delete(request, id):
    kind_to_delete = get_object_or_404(Kind, id =id )

    if "kindDelete" in request.POST :
        kind_to_delete.delete()
        messages.success(request, "تم حذف النوع بنجاح")
        return redirect("kinds")
#====================================================================================================================
def items(request):
    items = Item.objects.all().order_by("-date")
    kinds = Kind.objects.all()
    paginator = Paginator(items ,20)
    page = request.GET.get('page')
    try:
        item_list = paginator.page(page)
    except PageNotAnInteger:
        item_list = paginator.page(1)
    except EmptyPage :
        item_list = paginator.page(paginator.num_pages)

    if "addItem" in request.POST:
        name = request.POST.get('name')
        kind_name = request.POST.get('kind')
        prand = request.POST.get('prand')
        quantity = request.POST.get('quantity')
        price = request.POST.get('price')
        item_date = request.POST.get('date')
        if not item_date:
            item_date = date.today()

        item_id = request.POST.get('item_id', None)

        if Item.objects.filter(name=name).exclude(id=item_id).exists():
            messages.warning(request, f'المنتج ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("items")

        kind = Kind.objects.get(name=kind_name)
        Item.objects.create(name=name, kind=kind, prand=prand, quantity=quantity, price=price, date=item_date)
        messages.success(request, "تم اضافة صنف بنجاح")
        return redirect("items")
    
    elif 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        item_list = [Item.objects.get(pk = id) for id in results]
    
    context ={
        'items': item_list,
        'kinds': kinds,
    }
    return render(request, "items.html", context)
#====================================================================================================================
def item_delete(request, id):
    item_to_delete = get_object_or_404(Item, id =id )

    if "itemDelete" in request.POST :
        item_to_delete.delete()
        messages.success(request, "تم حذف المنتج بنجاح")
        return redirect("items")
#====================================================================================================================
def item_update(request, id):

    if 'itemUpdate' in request.POST:
        name = request.POST['name']
        kind_name = request.POST['kind_name']
        prand = request.POST['prand']
        quantity = request.POST['quantity']

        kind = Kind.objects.get(name=kind_name)

        if Item.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'المنتج ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("items")
        
        edit = Item.objects.get(id=id)
        edit.name = name
        edit.kind = kind
        edit.prand = prand
        edit.quantity = quantity
        edit.save()

        messages.success(request, 'تم تعديل بيانات الصنف بنجاح', extra_tags='success')
        return redirect("items")
    
    if 'itemUpdateShort' in request.POST:
        name = request.POST['name']
        kind_name = request.POST['kind_name']
        prand = request.POST['prand']
        quantity = request.POST['quantity']

        kind = Kind.objects.get(name=kind_name)

        if Item.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'المنتج ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("shorts")
        
        edit = Item.objects.get(id=id)
        edit.name = name
        edit.kind = kind
        edit.prand = prand
        edit.quantity = quantity
        edit.save()

        messages.success(request, 'تم تعديل بيانات الصنف بنجاح', extra_tags='success')
        return redirect("shorts")
#====================================================================================================================
def sale_page(request):
    items = Item.objects.all().order_by("-date")

    paginator = Paginator(items ,20)
    page = request.GET.get('page')
    try:
        items_list = paginator.page(page)
    except PageNotAnInteger:
        items_list = paginator.page(1)
    except EmptyPage :
        items_list = paginator.page(paginator.num_pages)

    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        items_list = [Item.objects.get(pk = id) for id in results]

    context ={
        "items" : items_list,
    }

    return render(request, "sales.html", context)
#====================================================================================================================
@login_required(login_url="login")
def sell(request, id):
    if "sell" in request.POST:
        item_id = request.POST.get('item')
        item = get_object_or_404(Item, pk=item_id)
        
        item_id = request.POST.get('item')
        sale_date = request.POST.get('date')  
        client_name = request.POST.get('client_name')
        client_phone = request.POST.get('client_phone')
        crash = request.POST.get('crash')
        paid = request.POST.get('paid')
        remain = request.POST.get('remain')
        method = request.POST.get('method')
        sale_price = request.POST.get('sale_price')
        sale_quantity = request.POST.get('sale_quantity')

        client_name = client_name.strip()

        sale_price = Decimal(sale_price)
        sale_quantity = Decimal(sale_quantity)
        paid = Decimal(paid)
        remain = Decimal(remain)

        if not client_name:
            client_name = "-"
        if not sale_date :
            sale_date = date.today()
        if sale_quantity > item.quantity:
            messages.error(request, "الكمية المباعة اكبر من الكمية المتبقية")
            return redirect("sales")
        if not paid:
            paid = 0
        if not crash:
            crash = "-"
        if not client_phone:
            client_phone = "-"
        if client_name :
            if Client.objects.filter(name=client_name).exclude(id=id).exists():
                client = Client.objects.get(name=client_name) 
                Sale.objects.create(client=client, item_id=item_id, date=sale_date, crash=crash,
                            sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                            client_phone=client_phone, method=method)
                Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
                messages.success(request, "تمت إضافة عملية بيع بنجاح")
                return redirect("sales")       

            else :
                try :
                    client = Client.objects.get(name=client_name)
                except Client.DoesNotExist:
                    client = Client.objects.create(name=client_name, phone = "-", opening_balance = 0, notes="-")
                    Sale.objects.create(client=client, item_id=item_id, date=sale_date, crash=crash,
                                sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                                client_phone=client_phone, method=method)
                    Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
                    messages.success(request, "تمت إضافة عملية بيع بنجاح")
                    return redirect("sales")       
            
        
        Sale.objects.create(client_name=client_name, item_id=item_id, date=sale_date, crash=crash,
                                   sale_price=sale_price, remain=remain, paid=paid, sale_quantity=sale_quantity,
                                   client_phone=client_phone, method=method)

        Item.objects.filter(id=item_id).update(quantity=F('quantity') - sale_quantity)
        Payment.objects.create(paid_money=paid)

        messages.success(request, "تمت إضافة عملية بيع بنجاح")
        return redirect("sales")       
#====================================================================================================================
def sale_update(request, id):

    if "saleUpdate" in request.POST:
        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        edit = Sale.objects.get(id=id)

        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()

        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("profits")  
    
    if "saleUpdate2" in request.POST:
        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        edit = Sale.objects.get(id=id)

        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()
        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("tempsales")  

    if "saleUpdate3" in request.POST:
        sale = get_object_or_404(Sale, id=id)
        client_id = sale.client.id

        client_name = request.POST["client_name"]
        paid = request.POST["paid"]
        method = request.POST["method"]

        edit = Sale.objects.get(id=id)
    
        edit.client_name = client_name
        edit.paid = paid
        edit.method = method
        edit.save()

        messages.success(request, 'تم تعديل بيانات العملية بنجاح', extra_tags='success')
        return redirect("clientpage", id= client_id)  
#====================================================================================================================
def sale_delete(request, id):
    sale_to_delete = get_object_or_404(Sale, id=id)

    if "saleDelete" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        sale_to_delete.delete()

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")    
    
    if "saleDelete2" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        sale_to_delete.delete()

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("tempsales")    

    if "saleDelete3" in request.POST:
        sale_quantity = sale_to_delete.sale_quantity
        item = sale_to_delete.item
        Item.objects.filter(id=item.id).update(quantity=F('quantity') + sale_quantity)
        sale_to_delete.delete()
        client_id = sale_to_delete.client.id

        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("clientpage" , id=client_id)    
#====================================================================================================================
def paid_done(request, id):
    sale_to_done = get_object_or_404(Sale, id=id)

    if "paidDone" in request.POST:
        total = sale_to_done.total
        sale_to_done.paid = total
        sale_to_done.remain = 0
        sale_to_done.save()

        messages.success(request, "تم تأكيد الدفع بنجاح")
        return redirect("tempsales")   
#====================================================================================================================
@login_required(login_url="login")
def clients(request):
    client = Client.objects.all()
    paginator = Paginator(client ,20)
    page = request.GET.get('page')
    try:
        client_list = paginator.page(page)
    except PageNotAnInteger:
        client_list = paginator.page(1)
    except EmptyPage :
        client_list = paginator.page(paginator.num_pages)

    if "addClient" in request.POST:
        name = request.POST.get("name")
        opening_balance = request.POST.get("opening_balance")
        phone = request.POST.get("phone")

        if Client.objects.filter(name=name).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("clients")
        
        if not opening_balance :
            opening_balance = 0

        Client.objects.create(name=name, opening_balance =opening_balance, phone=phone)
        messages.success(request, "تم اضافة عميل جديد بنجاح")
        return redirect("clients")


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Client.objects.all().filter(Q(name__icontains=search_input)).values()]
        client_list = [Client.objects.get(pk = id) for id in results]


    context = {"clients" : client_list}
    return render(request,"clients.html", context)
#====================================================================================================================
def client_update(request, id):

    if 'clientUpdate' in request.POST:
        name = request.POST['name']
        opening_balance = request.POST['opening_balance']
        phone = request.POST['phone']

        name = name.strip()
        old_client_data = Client.objects.filter(id=id).values().first()

        if Client.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'اسم العميل ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("clientpage", id=id)
        
        edit = Client.objects.get(id=id)

        edit.name = name
        edit.opening_balance = opening_balance
        edit.phone = phone
        edit.save()

        messages.success(request, 'تم تعديل بيانات العميل بنجاح', extra_tags='success')
        return redirect("clients")
#====================================================================================================================
def client_delete(request, id):
    client_to_delete = get_object_or_404(Client, id =id )

    if "clientDelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عميل',
            action_sort = 'حذف',
            model_affected=f'تم حذف العميل ({client_to_delete.name})',
        )
        client_to_delete.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("clients")
#====================================================================================================================
@login_required(login_url="login")
def client_page(request, id):
    items = Item.objects.all()
    client = get_object_or_404(Client, id=id)
    sales = Sale.objects.filter(client=client).order_by("-date")

    context = {"client": client, "sales": sales, "items":items}
    return render(request, "clientpage.html", context)
#====================================================================================================================
@login_required(login_url="login")
def profits(request):
    sales = Sale.objects.all().order_by("-date")
    paginator = Paginator(sales ,20)
    page = request.GET.get('page')
    try:
        sale_list = paginator.page(page)
    except PageNotAnInteger:
        sale_list = paginator.page(1)
    except EmptyPage :
        sale_list = paginator.page(paginator.num_pages)

    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Sale.objects.all().filter(Q(client_name__icontains=search_input)).values()]
        sale_list = [Sale.objects.get(pk = id) for id in results]

        
    context ={
        "sales" : sale_list,
    }
    return render(request,"profits.html", context)
#====================================================================================================================
def pay_update(request, id):
    old_pay_data = Payment.objects.values().get(id=id)

    if "payupdate" in request.POST:
        client = request.POST["client"]
        paid_money = request.POST["paid_money"]

        client = client.strip()

        paid_money = Decimal(paid_money)

        try:
            client_obj = Client.objects.get(name=client)
        except Client.DoesNotExist:
            messages.warning(request, f"اسم العميل ({client}) غير موجود   ")
            return redirect("profits")

        edit = Payment.objects.get(id=id)

        old_client = old_pay_data["client_id"]
        old_paid_money = old_pay_data["paid_money"]

        changes = []
        if client_obj.id != old_client:
            changes.append(f'اسم العميل من {Client.objects.get(id=old_client).name} إلى {client_obj.name}')
        if str(paid_money) != str(old_paid_money):
            changes.append(f'السعر من {old_paid_money} إلى {paid_money}')

        edit.client = client_obj
        edit.paid_money = paid_money
        edit.save()

        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='تعديل استلام نقدية',
            action_sort = 'تعديل',
            model_affected=f'تم تعديل عملية استلام نقدية: {", ".join(changes)}',
        )
        messages.success(request, 'تم تعديل بيانات التحصيل بنجاح', extra_tags='success')
        return redirect("profits")
#====================================================================================================================
def pay_delete(request, id):
    pay_to_delete = get_object_or_404(Payment, id =id )
    client_id = pay_to_delete.client.id

    if "paydelete" in request.POST :
        RecentAction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            action_type='حذف عملية دفع',
            action_sort = 'حذف',
            model_affected=f'تم حذف عملية دفع للعميل ({pay_to_delete.client.name}) و كانت بقيمة ({pay_to_delete.paid_money})',
        )
        pay_to_delete.delete()
        messages.success(request, "تم حذف العملية بنجاح")
        return redirect("profits")
#====================================================================================================================
def loses(request):
    loses = Lose.objects.all().order_by("-date")
    paginator = Paginator(loses ,20)
    page = request.GET.get('page')
    try:
        loses_list = paginator.page(page)
    except PageNotAnInteger:
        loses_list = paginator.page(1)
    except EmptyPage :
        loses_list = paginator.page(paginator.num_pages)

    if "addLose" in request.POST :
        lose_type = request.POST.get('lose_type')
        lose_money = request.POST.get('lose_money')
        lose_date = request.POST.get('date')
        notes = request.POST.get('notes')

        if not notes :
            notes = "-"

        elif not lose_date :
            lose_date = date.today()
        
        Lose.objects.create(lose_type=lose_type,lose_money=lose_money, date=lose_date, notes=notes)
        messages.success(request,"تم اضافة مصروف بنجاح")
        return redirect("loses")
    
    context ={
        'loses' : loses_list

    }

    return render(request,'loses.html', context)
#====================================================================================================================
def lose_delete(request, id):
    lose_to_delete = get_object_or_404(Lose, id =id )

    if "loseDelete" in request.POST :
        lose_to_delete.delete()
        messages.success(request, "تم حذف المصروف بنجاح")
        return redirect("loses")
#====================================================================================================================
def lose_update(request, id):

    if 'loseUpdate' in request.POST:
        lose_type = request.POST['lose_type']
        lose_money = request.POST['lose_money']
        notes = request.POST['notes']

           
        edit = Lose.objects.get(id=id)
        edit.lose_type = lose_type
        edit.lose_money = lose_money
        edit.notes = notes
        edit.save()

        messages.success(request, 'تم تعديل بيانات المصروف بنجاح', extra_tags='success')
        return redirect("loses")
#====================================================================================================================
def shorts(request):
    all_items = Item.objects.all().order_by("-date")
    shorts = [item for item in all_items if item.quantity == 0 ]
    paginator = Paginator(shorts, 30)

    page = request.GET.get('page')
    try:
        shorts_list = paginator.page(page)
    except PageNotAnInteger:
        shorts_list = paginator.page(1)
    except EmptyPage :
        shorts_list = paginator.page(paginator.num_pages)


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Item.objects.all().filter(Q(name__icontains=search_input)).values()]
        shorts_list = [Item.objects.get(pk = id) for id in results]

    context = {
        'items': shorts_list,
    }

    return render(request, 'shorts.html', context)
#====================================================================================================================
def tempsales(request):
    all_sales = Sale.objects.all().order_by("-date")
    tempsales = [sale for sale in all_sales if sale.remain > 0 ]
    paginator = Paginator(tempsales, 30)

    page = request.GET.get('page')
    try:
        temp_list = paginator.page(page)
    except PageNotAnInteger:
        temp_list = paginator.page(1)
    except EmptyPage :
        temp_list = paginator.page(paginator.num_pages)


    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Sale.objects.all().filter(Q(client_name__icontains=search_input)).values()]
        temp_list = [Sale.objects.get(pk = id) for id in results]

    context = {
        'sales': temp_list,
    }

    return render(request, 'tempsales.html', context)
#====================================================================================================================
def daycome(request):
    safe = get_object_or_404(Safe, id=1)
    all_daycoms = Daycome.objects.all().order_by("-date")
    paginator = Paginator(all_daycoms, 30)
    page = request.GET.get('page')
    try:
        comes_list = paginator.page(page)
    except PageNotAnInteger:
        comes_list = paginator.page(1)
    except EmptyPage:
        comes_list = paginator.page(paginator.num_pages)

    today = date.today()

    today_profits = Sale.objects.filter(date=today)
    total_profits = today_profits.aggregate(Sum('paid'))['paid__sum'] or 0

    today_loses = Lose.objects.filter(date=today)
    total_loses = today_loses.aggregate(Sum('lose_money'))['lose_money__sum'] or 0

    net_profit = total_profits - total_loses

    today_sales_with_win = Sale.objects.filter(date=today).annotate(win=ExpressionWrapper(F('sale_price') - F('item__price'), output_field=DecimalField())).values('win')
    total_win = today_sales_with_win.aggregate(Sum('win'))['win__sum'] or 0

    if "dayCome" in request.POST:
        total_profits = request.POST.get('total_profits')
        total_loses = request.POST.get('total_loses')
        date_str = request.POST.get('date')
        net_profit = request.POST.get('net_profit')
        win = request.POST.get('win')
        cash = request.POST.get('cash')
        wallet = request.POST.get('wallet')

        if Daycome.objects.filter(date=date_str).exists():
            messages.warning(request, f'تقفيل هذا اليوم محفوظ بالفعل في قاعدة البيانات')
            return redirect('daycome')

        Daycome.objects.create(loses=total_loses, income=total_profits, date=date_str, net_profit=net_profit, win = win , cash=cash, wallet=wallet)
        messages.success(request, "تم حفظ تقفيل اليوم")
        return redirect("daycome")

    elif 'search' in request.POST:
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Daycome.objects.all().filter(Q(date__icontains=search_input)).values()]
        comes_list = [Daycome.objects.get(pk=id) for id in results]

    context = {
        'total_profits': total_profits,
        'total_loses': total_loses,
        'net_profit': net_profit,
        'total_win': total_win,
        'today': today,
        'daycomes': comes_list,
        'today_profits': today_profits,
        'today_loses': today_loses,
        'safe': safe,
    }

    return render(request, 'daycome.html', context)
#====================================================================================================================
def daycome_delete(request, id):
    daycome_to_delete = get_object_or_404(Daycome, id =id )

    if "daycomeDelete" in request.POST :
        daycome_to_delete.delete()
        messages.success(request, "تم حذف التقفيل بنجاح")
        return redirect("daycome")
#====================================================================================================================
def daycome_update(request, id):

    if 'daycomeUpdate' in request.POST:
        total_profits = request.POST['total_profits']
        total_loses = request.POST['total_loses']
        net_profit = request.POST['net_profit']
        win = request.POST['win']
        cash = request.POST['cash']
        wallet = request.POST['wallet']
        date = request.POST['date']

        edit = Daycome.objects.get(id=id)
        edit.income = total_profits
        edit.loses = total_loses
        edit.net_profit = net_profit
        edit.win = win
        edit.cash = cash
        edit.wallet = wallet
        edit.date = date
        edit.save()

        messages.success(request, 'تم تعديل بيانات التقفيل بنجاح', extra_tags='success')
        return redirect("daycome")
#====================================================================================================================
def safe(request):
    safe_instance = get_object_or_404(Safe, id =1)
    cash_month = Sale.objects.filter(date__date=timezone.now().date(),method="نقدية").aggregate(Sum('paid'))['paid__sum'] or 0
    wallet_month = Sale.objects.filter(date__date=timezone.now().date(),method="محفظة").aggregate(Sum('paid'))['paid__sum'] or 0
    if request.method == 'POST':
        if 'deposit' in request.POST :
            amount = request.POST.get('amount')
            kind = request.POST.get('kind')
            amount = Decimal(amount)
            
            if kind == 'درج':  
                safe_instance.cash += amount
            elif kind == 'محفظة':  
                safe_instance.wallet += amount
            
            safe_instance.save()
            
            messages.success(request, "تم الايداع بنجاح")
            return redirect('safe') 
    
        if 'cashToWallet' in request.POST:
            ctw = Decimal(request.POST.get('ctw'))
            if safe_instance.cash >= ctw:
                safe_instance.cash -= ctw
                safe_instance.wallet += ctw
                safe_instance.save()
                messages.success(request, "تم الترحيل بنجاح")
            else:
                messages.error(request, "الرصيد الحالي غير كافي لهذه العملية")
            return redirect('safe')

        if 'walletToCash' in request.POST:
            wtc = Decimal(request.POST.get('wtc'))
            if safe_instance.wallet >= wtc:
                safe_instance.wallet -= wtc
                safe_instance.cash += wtc
                safe_instance.save()
                messages.success(request, "تم الترحيل بنجاح")
            else:
                messages.error(request, "الرصيد الحالي غير كافي لهذه العملية")
            return redirect('safe')

    context = {"safe" : safe_instance, "cash_month":cash_month, "wallet_month":wallet_month}

    return render(request,"safe.html", context)
#====================================================================================================================
def safe_update(request, id):

    if 'cashUpdate' in request.POST:
        cash = request.POST['cash']
        edit = Safe.objects.get(id=id)
        edit.cash = cash
        edit.save()
        messages.success(request, 'تم تعديل رصيد الدرج', extra_tags='success')
        return redirect("safe")

    if 'walletUpdate' in request.POST:
        wallet = request.POST['wallet']
        edit = Safe.objects.get(id=id)
        edit.wallet = wallet
        edit.save()
        messages.success(request, 'تم تعديل رصيد الدرج', extra_tags='success')
        return redirect("safe")
#====================================================================================================================
@login_required(login_url="login")
def suppliers(request):
    suppliers = Supplier.objects.all()
    paginator = Paginator(suppliers ,30)
    page = request.GET.get('page')
    try:
        supplier_list = paginator.page(page)
    except PageNotAnInteger:
        supplier_list = paginator.page(1)
    except EmptyPage :
        supplier_list = paginator.page(paginator.num_pages)

    if "addSupplier" in request.POST :
        name = request.POST.get('name')
        for_him = request.POST.get('for_him')
        phone = request.POST.get('phone')
        if Supplier.objects.filter(name=name).exists():
            messages.warning(request, f'اسم ألمورد ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("suppliers")

        Supplier.objects.create(name=name, for_him=for_him, phone=phone)
        messages.success(request,"تم اضافة مورد بنجاح")
        return redirect("suppliers")
    
    if 'search' in request.POST :
        search_input = request.POST.get('searchInput')
        results = [result['id'] for result in Supplier.objects.all().filter(Q(name__icontains=search_input)).values()]
        supplier_list = [Supplier.objects.get(pk = id) for id in results]

    context ={'suppliers': supplier_list}

    return render(request,"suppliers.html", context)
#====================================================================================================================
def supplier_update(request, id):

    if 'supplierUpdate' in request.POST:
        name = request.POST['name']
        for_him = request.POST['for_him']
        phone = request.POST['phone']

        name = name.strip()
        old_supplier_data = Supplier.objects.filter(id=id).values().first()

        if Supplier.objects.filter(name=name).exclude(id=id).exists():
            messages.warning(request, f'اسم المورد ({name}) موجود بالفعل في قاعدة البيانات')
            return redirect("suppliers")
        
        edit = Supplier.objects.get(id=id)

        edit.name = name
        edit.for_him = for_him
        edit.phone = phone
        edit.save()

        messages.success(request, 'تم تعديل بيانات المورد بنجاح', extra_tags='success')
        return redirect("suppliers")
#====================================================================================================================
def supplier_delete(request, id):
    supplier_to_delete = get_object_or_404(Supplier, id =id )

    if "supplierDelete" in request.POST :
        supplier_to_delete.delete()
        messages.success(request, "تم حذف العميل بنجاح")
        return redirect("suppliers")
#====================================================================================================================
