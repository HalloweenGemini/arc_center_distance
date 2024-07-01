let canvas = document.getElementById('imageCanvas');
let ctx = canvas.getContext('2d');
let points = [];
let mode = '3+3';
let pixelSpacing = [0.145, 0.145];
let originalImage = null;
let imageScale = 1;

document.getElementById('fileInput').addEventListener('change', function(e) {
    let file = e.target.files[0];
    let formData = new FormData();
    formData.append('file', file);

    fetch('/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        originalImage = new Image();
        originalImage.onload = function() {
            imageScale = 0.5 ;
            canvas.width = originalImage.width * imageScale;
            canvas.height = originalImage.height * imageScale;
            redrawCanvas();
        }
        originalImage.src = 'data:image/png;base64,' + data.image;
        pixelSpacing = data.pixelSpacing;
    });
});

canvas.addEventListener('click', function(e) {
    let rect = canvas.getBoundingClientRect();
    let x = (e.clientX - rect.left) / imageScale;
    let y = (e.clientY - rect.top) / imageScale;
    
    points.push([x, y]);
    redrawCanvas();

    if (mode === '3+3') {
        if (points.length === 3 || points.length === 6) {
            drawCircle(points.slice(-3), points.length > 3 ? 'blue' : 'red');
        }
        if (points.length === 6) {
            drawCenterLine();
        }
    } else if (mode === '3+2') {
        if (points.length === 3) {
            drawCircle(points, 'red');
        }
        if (points.length === 5) {
            drawCircle(points.slice(0, 3), 'red');
            drawCircle(points.slice(3), 'blue', calculateRadius(points.slice(0, 3)));
            drawCenterLine();
        }
    }
});

function redrawCanvas() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    if (originalImage) {
        ctx.drawImage(originalImage, 0, 0, canvas.width, canvas.height);
    }
    points.forEach((point, index) => {
        drawPoint(point[0] * imageScale, point[1] * imageScale, index < 3 ? 'red' : 'blue');
    });
    
    if (mode === '3+3') {
        if (points.length >= 3) {
            drawCircle(points.slice(0, 3), 'red');
        }
        if (points.length === 6) {
            drawCircle(points.slice(3), 'blue');
            drawCenterLine();
        }
    } else if (mode === '3+2') {
        if (points.length >= 3) {
            drawCircle(points.slice(0, 3), 'red');
        }
        if (points.length === 5) {
            let radius = calculateRadius(points.slice(0, 3));
            drawCircle(points.slice(3), 'blue', radius);
            drawCenterLine();
        }
    }
}


function drawPoint(x, y, color) {
    ctx.beginPath();
    ctx.arc(x, y, 3, 0, 2 * Math.PI);
    ctx.fillStyle = color;
    ctx.fill();
}

function drawCircle(points, color, fixedRadius = null) {
    let x1, y1, x2, y2, x3, y3;
    let a, b, c, x, y, r;

    if (fixedRadius === null) {
        [x1, y1] = points[0];
        [x2, y2] = points[1];
        [x3, y3] = points[2];

        a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2;
        b = (x1 * x1 + y1 * y1) * (y3 - y2) + (x2 * x2 + y2 * y2) * (y1 - y3) + (x3 * x3 + y3 * y3) * (y2 - y1);
        c = (x1 * x1 + y1 * y1) * (x2 - x3) + (x2 * x2 + y2 * y2) * (x3 - x1) + (x3 * x3 + y3 * y3) * (x1 - x2);

        x = -b / (2 * a);
        y = -c / (2 * a);
        r = Math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1));
    } else {
        [x1, y1] = points[0];
        [x2, y2] = points[1];
        r = fixedRadius;

        let q = Math.sqrt((x2 - x1)**2 + (y2 - y1)**2);
        if (q > 2 * r) {
            console.error("Distance between points is greater than the diameter");
            return;
        }

        let x3 = (x1 + x2) / 2;
        let y3 = (y1 + y2) / 2;
        let d = Math.sqrt(r**2 - (q / 2)**2);

        // 두 가능한 중심점 중 첫 번째 점을 선택합니다
        x = x3 + d * (y1 - y2) / q;
        y = y3 + d * (x2 - x1) / q;
    }

    ctx.beginPath();
    ctx.arc(x * imageScale, y * imageScale, r * imageScale, 0, 2 * Math.PI);
    ctx.strokeStyle = color;
    ctx.stroke();

    return [x, y, r]; // 중심점과 반지름을 반환
}

function drawCenterLine() {
    // console.log('drawCenterLine');
    let [x1, y1] = calculateCenter(points.slice(0, 3));
    let [x2, y2] = [];

    if (mode === '3+3') {
        [x2, y2] = calculateCenter(points.slice(3));
    } else if (mode === '3+2') {
        let radius = calculateRadius(points.slice(0, 3));
        let [c1, c2] = defineCircle2(points[3], points[4], radius);
        // 두 개의 중심 중 첫 번째 중심을 선택합니다
        [x2, y2] = c1;
    }

    ctx.beginPath();
    ctx.moveTo(x1 * imageScale, y1 * imageScale);
    ctx.lineTo(x2 * imageScale, y2 * imageScale);
    ctx.strokeStyle = 'white';
    ctx.stroke();

    let distance = Math.sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1));
    let realDistance = distance * pixelSpacing[0];  // Assuming isotropic pixels
    document.getElementById('distanceLabel').textContent = `거리: ${realDistance.toFixed(2)} mm`;
}

function defineCircle2(p1, p2, radius) {
    let [x1, y1] = p1;
    let [x2, y2] = p2;

    let q = Math.sqrt((x2 - x1)**2 + (y2 - y1)**2);
    if (q > 2 * radius) {
        console.error("Distance between points is greater than the diameter");
        return [];
    }

    let x3 = (x1 + x2) / 2;
    let y3 = (y1 + y2) / 2;

    let d = Math.sqrt(radius**2 - (q / 2)**2);
    let c1 = [x3 + d * (y1 - y2) / q, y3 + d * (x2 - x1) / q];
    let c2 = [x3 - d * (y1 - y2) / q, y3 - d * (x2 - x1) / q];

    return [c1, c2];
}

function calculateRadius(points) {
    let [x1, y1] = points[0];
    let [x2, y2] = points[1];
    let [x3, y3] = points[2];

    let a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2;
    let b = (x1 * x1 + y1 * y1) * (y3 - y2) + (x2 * x2 + y2 * y2) * (y1 - y3) + (x3 * x3 + y3 * y3) * (y2 - y1);
    let c = (x1 * x1 + y1 * y1) * (x2 - x3) + (x2 * x2 + y2 * y2) * (x3 - x1) + (x3 * x3 + y3 * y3) * (x1 - x2);

    let x = -b / (2 * a);
    let y = -c / (2 * a);

    return Math.sqrt((x - x1) * (x - x1) + (y - y1) * (y - y1));
}
function calculateCenter(points) {
    let [x1, y1] = points[0];
    let [x2, y2] = points[1];
    let [x3, y3] = points[2];

    let a = x1 * (y2 - y3) - y1 * (x2 - x3) + x2 * y3 - x3 * y2;
    let b = (x1 * x1 + y1 * y1) * (y3 - y2) + (x2 * x2 + y2 * y2) * (y1 - y3) + (x3 * x3 + y3 * y3) * (y2 - y1);
    let c = (x1 * x1 + y1 * y1) * (x2 - x3) + (x2 * x2 + y2 * y2) * (x3 - x1) + (x3 * x3 + y3 * y3) * (x1 - x2);

    let x = -b / (2 * a);
    let y = -c / (2 * a);

    return [x, y];
}

document.getElementById('resetButton').addEventListener('click', function() {
    points = [];
    redrawCanvas();
    document.getElementById('distanceLabel').textContent = '거리: N/A';
});

document.getElementById('undoButton').addEventListener('click', function() {
    if (points.length > 0) {
        points.pop();
        redrawCanvas();
    }
});

document.getElementById('mode3_3Button').addEventListener('click', function() {
    mode = '3+3';
    resetPoints();
});

document.getElementById('mode3_2Button').addEventListener('click', function() {
    mode = '3+2';
    resetPoints();
});

function resetPoints() {
    points = [];
    redrawCanvas();
    document.getElementById('distanceLabel').textContent = '거리: N/A';
}
