let W = 800;
let H = 600;
let R = 10;
let P = 10;
let D = 2*Math.sqrt(P);

let state; 

function setup() {
    createCanvas(W, H);

    state = {
        pos: createVector(0,0),
        vel: createVector(0,0),
        g: undefined,
    }
};

}

function update() {
    let ddy = p5.Vector.mult(state.vel, -D);

    if (state.g !== undefined) {
        let err = p5.Vector.sub(state.g, state.pos);

        ddy = p5.Vector.add(ddy, p5.Vector.mult(err, P));
    }
}

function draw() {
    background("black");

    //if 
}
