const W = 800;
const H = 600;

const oscilloscopeW = 250;
const oscilloscopeH = Math.round(oscilloscopeW / 1.62);

const markerSize = 30;

const worldToCanvasScale = 600;
const canvasToWorldScale = 1./worldToCanvasScale;

const defaults = {
    az: 10,
    bz: 10/4,
    forcingTerm: "none",
    criticallyDamped: false,
    pause: false,
    goal_x: undefined,
    goal_y: undefined,
};

let controlPanel;
let sliderAz;
let sliderBz;
let checkboxCriticallyDamped;
let checkboxPause;
let forcingTermSelect;

let state;

let oscilloscopeX;
let oscilloscopeY;

function setup() {
    createCanvas(W, H);

    let g = undefined;
    if (defaults.goal_x !== undefined && defaults.goal_y !== undefined)
    {
        g = createVector(defaults.goal_x, defaults.goal_y);
    }

    state = {
        t: 0,
        pos: createVector(0,0),
        vel: createVector(0,0),
        g: g,
    };

    controlPanel = createDiv('');
    controlPanel.position(10,10);
    controlPanel.style('background', 'rgb(50,50,50)');
    controlPanel.style('padding', '10px');
    controlPanel.style('display', 'flex');
    controlPanel.style('align-items', 'center');
    controlPanel.style('gap', '10px');
    controlPanel.style('border', '1px solid white');
    controlPanel.style('color', 'white');
    //controlPanel.draggable();

    sliderAz = createSlider(0, 50, defaults.az);
    sliderAz.parent(controlPanel);
    sliderAz.changed(sliderAzCallback);
    createSpan("&alpha;<sub>z</sub>").parent(controlPanel);

    sliderBz = createSlider(0, 50, defaults.bz);
    sliderBz.parent(controlPanel);
    createSpan("&beta;<sub>z</sub>").parent(controlPanel);

    forcingTermSelect = createSelect()
    forcingTermSelect.parent(controlPanel);
    forcingTermSelect.option("No forcing term", "none");
    forcingTermSelect.option("Sinusoid", "sinusoid");
    forcingTermSelect.option("Vanishing sinusoid", "vanishing");
    forcingTermSelect.selected(defaults.forcingTerm);
    forcingTermSelect.changed(resetTime);

    checkboxCriticallyDamped = createCheckbox("Crit. damped", defaults.criticallyDamped);
    checkboxCriticallyDamped.parent(controlPanel);
    checkboxCriticallyDamped.changed(enableOrDisableCriticallyDamped);

    checkboxPause = createCheckbox("Pause", defaults.pause);
    checkboxPause.parent(controlPanel);

    enableOrDisableCriticallyDamped();
    sliderAzCallback();

    oscilloscopeX = new Oscilloscope({
        width: oscilloscopeW,
        height: oscilloscopeH,
        x0: W-oscilloscopeW-10,
        y0: 100,
        dt: 1.0 / getTargetFrameRate(),
        T: 2.0,
        A: 1.5,
        title: "x",
    });

    oscilloscopeY = new Oscilloscope({
        width: oscilloscopeW,
        height: oscilloscopeH,
        x0: W-oscilloscopeW-10,
        y0: 100 + oscilloscopeH + 50,
        dt: 1.0 / getTargetFrameRate(),
        T: 2.0,
        A: 1.0,
        title: "y",
    });
}

function resetTime() {
    state.t = 0;
}

function enableOrDisableCriticallyDamped() {
    if (checkboxCriticallyDamped.checked()) {
        sliderBz.attribute("disabled", "");
        forceCriticallyDamped();
    }
    else {
        sliderBz.removeAttribute("disabled");
    }
}

function sliderAzCallback() {
    if (checkboxCriticallyDamped.checked()) {
        forceCriticallyDamped();
    }
}

function forceCriticallyDamped() {
    sliderBz.value(sliderAz.value() / 4);
}

function worldToCanvasCoords(arg1, arg2=undefined) {
    let x;
    let y;
    if (arg2 === undefined) {
        x = arg1.x;
        y = arg1.y;
    }
    else {
        x = arg1;
        y = arg2;
    }
    return createVector(worldToCanvasScale*x+W/2, H/2-worldToCanvasScale*y);
}

function canvasToWorldCoords(arg1, arg2=undefined) {
    let x;
    let y;
    if (arg2 === undefined) {
        x = arg1.x;
        y = arg1.y;
    }
    else {
        x = arg1;
        y = arg2;
    }
    return createVector((x-W/2)*canvasToWorldScale, (H/2-y)*canvasToWorldScale);
}

function drawCross(x, y, size) {
    line(x-size/2, y-size/2, x+size/2, y+size/2);
    line(x-size/2, y+size/2, x+size/2, y-size/2);
}

function forcingTerm(vanishingFactor) {
    let t = state.t;
    let fade = exp(-vanishingFactor*t);
    let fx = -TWO_PI*TWO_PI*cos(TWO_PI*t)*fade;
    let fy = TWO_PI*TWO_PI*sin(TWO_PI*t)*fade;
    return createVector(fx, fy);
}

function update(dt) {
    let P = sliderAz.value()*sliderBz.value();
    let D = sliderAz.value();
    
    let ddy = p5.Vector.mult(state.vel, -D);

    if (forcingTermSelect.selected() === "sinusoid") {
        ddy.add(forcingTerm(0));
    }
    else if (forcingTermSelect.selected() === "vanishing") {
        ddy.add(forcingTerm(1));
    }

    if (state.g !== undefined) {
        let err = p5.Vector.sub(state.g, state.pos);

        ddy = p5.Vector.add(ddy, p5.Vector.mult(err, P));
    }

    state.t += dt;
    state.vel.add(p5.Vector.mult(ddy, dt));
    state.pos.add(p5.Vector.mult(state.vel, dt));
}

function doubleClicked() {
    state.g = canvasToWorldCoords(mouseX, mouseY);
    if (forcingTermSelect.selected() === "vanishing") {
        resetTime();
    }
    oscilloscopeX.add_horizontal_ruler(state.g.x, "red");
    oscilloscopeY.add_horizontal_ruler(state.g.y, "red");
}

function keyReleased() {
    if (key === 'p') {
        let currentValue = checkboxPause.checked();
        checkboxPause.checked(!currentValue);
    }
}

window.addEventListener("message", function(event) {
    let data = event.data;
    if (data.action === "setPause") {
        checkboxPause.checked(data.value);
    }
    else if (data.action === "setAz") {
        sliderAz.value(data.value);
        sliderAzCallback();
    }
    else if (data.action === "setBz") {
        sliderBz.value(data.value);
    }
    else if (data.action === "setForcingTerm") {
        forcingTermSelect.selected(data.value);
    }
    else if (data.action === "setCriticallyDamped") {
        checkboxCriticallyDamped.checked(data.value);
        enableOrDisableCriticallyDamped();
    }
    else if (data.action === "setGoal") {
        state.g = createVector(data.xvalue, data.yvalue);
    }
});

function draw() {
    background("black");

    posCanvas = worldToCanvasCoords(state.pos);

    noStroke();
    fill(200);
    circle(posCanvas.x, posCanvas.y, markerSize);

    if (state.g !== undefined) {
        stroke("red");
        strokeWeight(1);
        goalCanvas = worldToCanvasCoords(state.g);
        drawCross(goalCanvas.x, goalCanvas.y, markerSize);
    }

    oscilloscopeX.draw();
    oscilloscopeY.draw();

    if (!checkboxPause.checked()) {
        update(1 / getTargetFrameRate());
        oscilloscopeX.push(state.pos.x);
        oscilloscopeY.push(state.pos.y);
    }
}
