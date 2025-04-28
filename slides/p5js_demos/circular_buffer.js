

class CircularBuffer {
    data;
    length;
    head;

    constructor(capacity) {
        this.data = new Array(capacity);
        this.length = 0;
        this.head = 0;
    }

    capacity() {
        return this.data.length;
    }

    at(index) {
        return this.data[(this.head + index)%this.data.length];
    }

    front() {
        return this.at(0);
    }

    back() {
        return this.at(this.length-1);
    }

    back_index() {
        return (this.head + this.length - 1) % this.data.length;
    }

    push(element) {
        if (this.length === this.data.length) {
            this.data[this.head] = element;
            this.head++;
            if (this.head === this.data.length) {
                this.head = 0;
            }
        }
        else {
            this.data[(this.head + this.length)%this.data.length] = element;
            this.length++;
        }
    }

    pop() {
        if (this.length === 0)
        {
            return undefined;
        }
        var back_element = this.back();
        this.data[this.back_index()] = undefined;
        this.length--;
        return back_element;
    }

    shift() {
        if (this.length === 0) {
            return undefined;
        }
        var front_element = this.front();
        this.data[this.head] = undefined;
        this.length--;
        this.head++;
        if (this.head === this.data.length) {
            this.head = 0;
        }
        return front_element;
    }

}

