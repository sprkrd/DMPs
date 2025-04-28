
function dashed_line(x0, y0, x1, y1, dash_length) {
    dx = x1 - x0;
    dy = y1 - y0;
    line_length = mag(dx, dy);
    dx = (dx / line_length) * dash_length;
    dy = (dy / line_length) * dash_length;
    x = x0;
    y = y0;
    while (dx*(x1-x) + dy*(y1-y) > 0) {
        line(x, y, x + dx, y + dy);
        x += 2*dx;
        y += 2*dy;
    }
}
