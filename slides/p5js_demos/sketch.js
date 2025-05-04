let W = 800;
let H = 600;

let oscilloscopeW = 250;
let oscilloscopeH = Math.round(oscilloscopeW / 1.62);

let markerSize = 30;

let worldToCanvasScale = 600;
let canvasToWorldScale = 1./worldToCanvasScale;

let controlPanel;
let sliderAz;
let sliderBz;
let checkboxCriticallyDamped;
let checkboxPause;

let state;

let oscilloscopeX;
let oscilloscopeY;

function setup() {
    createCanvas(W, H);

    state = {
        pos: createVector(0,0),
        vel: createVector(0,0),
        g: undefined,
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

    sliderAz = createSlider(0, 50, 10);
    sliderAz.parent(controlPanel);
    sliderAz.changed(sliderAzCallback);
    createSpan("Az").parent(controlPanel);

    sliderBz = createSlider(0, 50, 10/4);
    sliderBz.parent(controlPanel);
    createSpan("Bz").parent(controlPanel);

    checkboxCriticallyDamped = createCheckbox("Crit. damped", false);
    checkboxCriticallyDamped.parent(controlPanel);
    checkboxCriticallyDamped.changed(enableOrDisableCriticallyDamped);

    checkboxPause = createCheckbox("Pause", false);
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
    });

    oscilloscopeY = new Oscilloscope({
        width: oscilloscopeW,
        height: oscilloscopeH,
        x0: W-oscilloscopeW-10,
        y0: 100 + oscilloscopeH + 50,
        dt: 1.0 / getTargetFrameRate(),
        T: 2.0,
        A: 1.0,
    });
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

function update(dt) {
    let P = sliderAz.value()*sliderBz.value();
    let D = sliderAz.value();
    
    let ddy = p5.Vector.mult(state.vel, -D);

    if (state.g !== undefined) {
        let err = p5.Vector.sub(state.g, state.pos);

        ddy = p5.Vector.add(ddy, p5.Vector.mult(err, P));
    }

    state.vel.add(p5.Vector.mult(ddy, dt));
    state.pos.add(p5.Vector.mult(state.vel, dt));
}

function doubleClicked() {
    state.g = canvasToWorldCoords(mouseX, mouseY);
    oscilloscopeX.add_horizontal_ruler(state.g.x, "red");
    oscilloscopeY.add_horizontal_ruler(state.g.y, "red");
}

function keyReleased() {
    if (key === 'p') {
        let currentValue = checkboxPause.checked();
        checkboxPause.checked(!currentValue);
    }
}

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
