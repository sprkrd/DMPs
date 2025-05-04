

class Oscilloscope {
    config;
    #data;
    #background = undefined;
    #hrule = undefined;

    constructor(config = {}) {
        this.config = {
            width: 200,
            height: 100,
            x0: 0,
            y0: 0,
            dt: 0.02,
            T: 1,
            A: 4,
            n_horizontal_divisions: 7,
            n_vertical_divisions: 3,
            ...config
        };
        this.#data = new CircularBuffer(Math.floor(this.config.T/this.config.dt));
    }

    push(element) {
        this.#data.push(element);
    }

    redraw_background() {
        this.#background = undefined;
    }

    _draw_background() {
        let config = this.config;
        if (this.#background === undefined) {
            this._draw_canvas();
            this._draw_grid();
            
            this.#background = get(config.x0-1, config.y0-1, config.width+2, config.height+2);
        }
        else {
            image(this.#background, config.x0-1, config.y0-1);
        }
    }

    _draw_canvas() {
        let config = this.config;

        strokeWeight(1);
        stroke(255);
        fill(32);

        rect(config.x0, config.y0, config.width, config.height);
    }

    _draw_grid() {
        let config = this.config;

        let h_gap = config.width / (config.n_horizontal_divisions + 1);
        let v_gap = config.height / (config.n_vertical_divisions + 1);

        let x_max = config.x0 + config.width;
        let y_max = config.y0 + config.height;

        strokeWeight(1);
        stroke(127);

        for (let i = 1; i <= config.n_horizontal_divisions; i++) {
            let x = config.x0 + i*h_gap;
            dashed_line(x, config.y0, x, y_max, 4);
        }

        for (let i = 1; i <= config.n_vertical_divisions; i++) {
            let y = config.y0 + i*v_gap;
            dashed_line(config.x0, y, x_max, y, 4);
        }

        let baseline = config.y0 + config.height/2;
    }

    _convert_y_value(y) {
        let config = this.config;
        let ymin = config.y0;
        let ymax = ymin + config.height;
        let mag_to_ycoord = config.height/config.A;
        let baseline = config.y0 + config.height/2;
        return constrain(baseline - y*mag_to_ycoord, ymin, ymax);
    }

    _draw_signal() {
        if (this.#data.length < 2) return;
        let config = this.config;
        let idx_to_xcoord = config.dt*config.width/config.T;
        noFill();
        stroke(255);
        strokeWeight(1);
        beginShape();
        for (let i = 0; i < this.#data.length; i++) {
            x = config.x0 + i*idx_to_xcoord;
            y = this._convert_y_value(this.#data.at(i));
            vertex(x, y);
        }
        endShape();
    }

    _draw_hrule() {
        let config = this.config;
        let x0 = config.x0;
        let x1 = config.x0 + config.width;
        let y = this._convert_y_value(this.#hrule.y);

        stroke(this.#hrule.color);
        strokeWeight(1);
        dashed_line(x0, y, x1, y, 4);
    }

    add_horizontal_ruler(y, c) {
        this.#hrule = {
            y: y,
            color: c,
        };
    }

    draw() {
        var baseline = this.y0 + this.height/2;
        this._draw_background();
        this._draw_signal();
        if (this.#hrule !== undefined) {
            this._draw_hrule();
        }
    }
}


