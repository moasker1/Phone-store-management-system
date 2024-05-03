

//defining html elements
const sellsdel = document.querySelectorAll('#sellsdel')
const sellsup = document.querySelectorAll('#sellsup')
const windowcon = document.getElementById('windowcon')
const closedetwin = document.getElementById('closedetwin')
let todaydate = document.getElementById('todaydate')
let price = document.getElementById('price');
//-----------------------------------------------------------------------------------------------------------
// Get all date input elements
const dateInputs = document.querySelectorAll('input[type="date"]');
// Get today's date
const today = new Date();
// Loop through each input and set its value to today's date
dateInputs.forEach(input => {
    input.value = today.toISOString().split('T')[0];
});
//-----------------------------------------------------------------------------------------------------------

sellsdel.forEach((sellsdel)=>{
    sellsdel.onclick=()=>{
        const metadata = sellsdel.getAttribute('metadata')
        windowcon.style.visibility = 'visible'
        windowcon.style.opacity = '1'
        document.getElementById('detailcontainer').innerHTML=metadata
        
    }
})
sellsup.forEach((sellsup)=>{
    sellsup.onclick=()=>{
        const metadata = sellsup.getAttribute('metadata')
        windowcon.style.visibility = 'visible'
        windowcon.style.opacity = '1'
        document.getElementById('detailcontainer').innerHTML=metadata
    }
})
closedetwin.addEventListener('click',()=>{
    windowcon.style.top='0'
    windowcon.style.visibility='hidden'
    windowcon.style.opacity='0'
})
//-----------------------------------------------------------------------------------------------------------
const billbtn = document.getElementById('billbtn');
billbtn.onclick=()=>{
    const metadata = billbtn.getAttribute('metadata')
    windowcon.style.visibility = 'visible'
    windowcon.style.opacity = '1'
    document.getElementById('detailcontainer').innerHTML=metadata
}
function add_prods(){
    const prod_input = document.getElementById('prod_input')
    const kind_input = document.getElementById('kind_input')
    const date_input = document.getElementById('date_input')
    const quant_input = document.getElementById('quant_input')
    const price_input = document.getElementById('price_input')
    const pay_input = document.getElementById('pay_input')
    const billmakebtn = document.getElementById('billmakebtn')
    //create product
    var prodata;
    let mood ="create";
    if(localStorage.product != null){
        prodata= JSON.parse(localStorage.product);
    }else{
        prodata=[];
    }
    let newpro ={
        title:prod_input.value.toLowerCase(),
        kind:kind_input.value,
        date:date_input.value,
        quant:quant_input.value,
        price:price_input.value,
        pay:pay_input.value,
        remain:parseFloat((price_input.value*quant_input.value)-pay_input.value),
    }
    //counting
    if(mood==='create'){
        prodata.push(newpro);
    }else{
        prodata[tmp]=newpro;
        mood='create';
        create.innerHTML='Create';
        count.style.display='block';
    }
    localStorage.setItem('product',JSON.stringify(prodata));
    //clear data
    prod_input.value='';
    kind_input.value='';
    date_input.value='';
    quant_input.value='';
    price_input.value='';
    pay_input.value='';
    let table ='';
    for(i=0 ; i< prodata.length; i++){
        table +=`
        <tr>
            <td>${i}</td>
            <td>${prodata[i].title}</td>
            <td>${prodata[i].kind}</td>
            <td>${prodata[i].date}</td>
            <td>${prodata[i].quant}</td>
            <td>${prodata[i].price}</td>
            <td>${prodata[i].pay}</td>
            <td>${prodata[i].remain}</td>
            <td><button onclick="updateData(${i})">update</button></td>
            <td><button onclick="deleteData(${i})">remove</button></td>
        </tr>`;
    }
    document.getElementById('prods_table').innerHTML= table;
//     //delete items
//     function deleteData(i){
//         prodata.splice(i,1);
//         localStorage.product= JSON.stringify(prodata);
    
//         showData();
//     }
//     //delete all itmes
//     function deleteAll(){
//         localStorage.clear();
//         prodata.splice(0);
//         showData();
//     }
//     //update data
//     function updateData(i){
//         title.value = prodata[i].title;
//         price.value = prodata[i].price;
//         taxis.value = prodata[i].taxis;
//         ads.value = prodata[i].ads;
//         discount.value = prodata[i].discount;
//         category.value = prodata[i].category;
//         create.innerHTML='Update';
//         count.style.display='none';
//         mood='update';
//         tmp=i;
//         geTotal();
//         scroll({
//             top:0,
//             behavior:'smooth'
//         })
}
//-----------------------------------------------------------------------------------------------------------
