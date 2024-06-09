var admin = document.querySelectorAll('.id1'),
    moder = document.querySelectorAll('.id2'),
    user = document.querySelectorAll('.id3');
var select = document.myform.selectedUsers;
var UserID = document.querySelectorAll('.UserID')
var items = document.querySelectorAll('.UserFIO');


var find = document.find.submitFind;

// UserID.forEach((uid) => {
//     uid.closest('.Users').addEventListener('click', (e) => {
//         console.log("Меня нажали + " + uid.innerText);
//         let str = "messages/" + uid.innerText;
//         window.location.href = str;
//     })
// })

function changeOption() {
    const sel = select.options[select.selectedIndex];
    console.log(sel.text)
    if (sel.text == "Пользователи") {
        admin.forEach((a) => {
            a.closest('.Users').classList.add('invise');
        })
        moder.forEach((m) => {
            m.closest('.Users').classList.add('invise');
        })
        user.forEach((u) => {
            u.closest('.Users').classList.remove('invise');
        })
    }
    if (sel.text == "Администраторы") {
        admin.forEach((a) => {
            a.closest('.Users').classList.remove('invise');
        })
        moder.forEach((m) => {
            m.closest('.Users').classList.add('invise');
        })
        user.forEach((u) => {
            u.closest('.Users').classList.add('invise');
        })
    }
    if (sel.text == "Модераторы") {
        admin.forEach((a) => {
            a.closest('.Users').classList.add('invise');
        })
        moder.forEach((m) => {
            m.closest('.Users').classList.remove('invise');
        })
        user.forEach((u) => {
            u.closest('.Users').classList.add('invise');
        })
    }
    if (sel.text == "Все аккаунты") {
        admin.forEach((a) => {
            a.closest('.Users').classList.remove('invise');
        })
        moder.forEach((m) => {
            m.closest('.Users').classList.remove('invise');
        })
        user.forEach((u) => {
            u.closest('.Users').classList.remove('invise');
        })
    }
}

select.addEventListener("change", changeOption);

find.addEventListener('click', (e) => {

    e.preventDefault();
    items.forEach((item) => {
        item.closest('.Users').classList.remove('invise');
    })
    var findText = document.find.textFind.value;
    console.log(findText)
    if (~findText.indexOf("<gl3_")) {
        UserID.forEach((id) => {
            console.log(id.innerText)
            if (id.innerText == findText) {
                id.closest('.Users').classList.remove('invise');
            } else {
                id.closest('.Users').classList.add('invise');
            }
        })
    } else {
        items.forEach((item) => {
            console.log(item.innerText)
            if (item.innerText.indexOf(findText)) {
                item.closest('.Users').classList.add('invise');
            } else {
                item.closest('.Users').classList.remove('invise');
            }
        })
    }

})