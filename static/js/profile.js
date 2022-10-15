
var swiper = new Swiper(".dest_add", {
    spaceBetween: 30,
    pagination: {
        el: ".swiper-pagination",
        clickable: true,
    },
});
var swiper = new Swiper(".top_des_container", {
    spaceBetween: 20,
    loop: true,
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
    breakpoints: {
        640: {
            slidesPerView: 1,
        },
        768: {
            slidesPerView: 3,
        },
        1024: {
            slidesPerView: 4,
        },
    },
});


var swiper = new Swiper(".brand-container", {
    spaceBetween: 20,
    loop: true,
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
    breakpoints: {
        450: {
            slidesPerView: 2,
        },
        768: {
            slidesPerView: 3,
        },
        991: {
            slidesPerView: 4,
        },
        1200: {
            slidesPerView: 5,
        },
    },
});

var swiper = new Swiper(".testimonial_div", {
    spaceBetween: 20,
    loop: true,
    autoplay: {
        delay: 2500,
        disableOnInteraction: false,
    },
    breakpoints: {
        640: {
            slidesPerView: 1,
        },
        768: {
            slidesPerView: 2,
        },
        1024: {
            slidesPerView: 3,
        },
    },
});


// Profile page

document.getElementById("profile").style.display = "block";
document.getElementById("doc").style.display = "none";
document.getElementById("start").style.display = "none";
document.getElementById("go").style.display = "none";
document.getElementById("complete").style.display = "none";

function profile() {
    document.getElementById("profile").style.display = "block";
    document.getElementById("doc").style.display = "none";
    document.getElementById("start").style.display = "none";
    document.getElementById("go").style.display = "none";
    document.getElementById("complete").style.display = "none";

}
function documents() {
    document.getElementById("profile").style.display = "none";
    document.getElementById("doc").style.display = "block";
    document.getElementById("start").style.display = "none";
    document.getElementById("go").style.display = "none";
    document.getElementById("complete").style.display = "none";

}
function started(){
    document.getElementById("profile").style.display = "none";
    document.getElementById("doc").style.display = "none";
    document.getElementById("start").style.display = "block";
    document.getElementById("go").style.display = "none";
    document.getElementById("complete").style.display = "none";


}
function going(){
    document.getElementById("profile").style.display = "none";
    document.getElementById("doc").style.display = "none";
    document.getElementById("go").style.display = "block";
    document.getElementById("start").style.display = "none";
    document.getElementById("complete").style.display = "none";

} 
function complete(){
    document.getElementById("profile").style.display = "none";
    document.getElementById("doc").style.display = "none";
    document.getElementById("start").style.display = "none";
    document.getElementById("go").style.display = "none";
    document.getElementById("complete").style.display = "block";

}
