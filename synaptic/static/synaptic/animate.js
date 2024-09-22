function animate(msg) {
    if (msg.animation == "expand_from_centre") {
        gsap.from('.animation', {scaleX:0, scaleY:0, duration:1});
    }
    if (msg.animation == "fade_in") {
        gsap.from('.animation', {autoAlpha:0, duration:1});
    }
    if (msg.animation == "horizontal_grow") {
        var animation = gsap.timeline();
        animation
            .from('.animation', {scaleX:0, transformOrigin: "center", duration:1})
            .from('.animation', {autoAlpha:0, duration:1}, "<");
    }
    if (msg.animation == "rotate_grow_in") {
        gsap.from('.animation', {scaleX:0, scaleY:0, rotate:270, transformOrigin: "50% 50%"});
    }
    if (msg.animation == "swipe_from_right") {
        gsap.from('.animation', {scaleX:0, transformOrigin:"right", duration:1});
    }
    if (msg.animation == "swipe_from_left") {
        gsap.from('.animation', {scaleX:0, transformOrigin:"left", duration:1});
    }
    if (msg.animation == "swipe_from_top") {
        gsap.from('.animation', {scaleY:0, transformOrigin:"top", duration:1});
    }
    if (msg.animation == "swipe_from_bottom") {
        gsap.from('.animation', {scaleY:0, transformOrigin:"bottom", duration:1});
    }
    if (msg.animation == "swipe_from_top_left") {
        gsap.from('.animation', {scaleX:0, scaleY:0, transformOrigin:"top left", duration:1});
    }
    if (msg.animation == "swipe_from_bottom_left") {
        gsap.from('.animation', {scaleX:0, scaleY:0, transformOrigin:"bottom left", duration:1});
    }
    if (msg.animation == "swipe_from_top_right") {
        gsap.from('.animation', {scaleX:0, scaleY:0, transformOrigin:"top right", duration:1});
    }
    if (msg.animation == "swipe_from_bottom_right") {
        gsap.from('.animation', {scaleX:0, scaleY:0, transformOrigin:"bottom right", duration:1});
    }
    if (msg.animation == "scroll") {
        var animation = gsap.timeline();
        animation
            .set('.animation', {opacity: 0})
            .from('.animation-container', {scaleX:0, transformOrigin: "left", duration:0.5})
            .from('.animation', {scaleX:0, transformOrigin:"left", duration:0.5})
            .fromTo('.animation', {opacity:0}, {opacity:1, duration:0.5}, '<')
    }
}

function explode(container, element, qty, scale, childScale) {
    var containerElem = document.querySelector(container);
    var dots = gsap.timeline();
    dots.fromTo(containerElem, {scaleX:0, scaleY: 0}, {scaleX:scale, scaleY: scale, duration:2});
    var elementElem = document.querySelector(element)
    for (i = 0; i < qty; i++) {
        var numX = Math.round(random(-10, 10)) * 100;
        var numY = Math.round(random(-10, 10)) * 100;
        child = $(elementElem).clone().appendTo(containerElem);
        dots.to(elementElem, 0.5, {
                scale: 0,
                autoAlpha: 0,
                duration: 0
            }, 2)

        dots.fromTo(child, 1, {scaleX:0, scaleY:0}, {
            x: numX,
            y: numY,
            scaleX:childScale,
            scaleY:childScale,
            autoAlpha: 0,
            duration: 2
        }, 2);
    }
}

//return positive or negative integar
function random(min, max) {
    return min + Math.random() * (max - min);
}