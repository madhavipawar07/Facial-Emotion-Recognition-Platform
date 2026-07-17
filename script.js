async function uploadToAWS(image) {

    loading.style.display = "block";

    try {

        const base64Image = image.split(",")[1];

        const response = await fetch(
            "https://84cnrwdtu6.execute-api.ap-south-1.amazonaws.com/upload", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json"
                },
                body: JSON.stringify({
                    image: base64Image
                })
            }
        );

        if (!response.ok) {
            const errorText = await response.text();
            throw new Error(errorText);
        }

        const data = await response.json();

console.log("API Response:", data);

loading.style.display = "none";

updateResults(data);

    } catch (error) {

        loading.style.display = "none";

        console.error(error);

        alert("Upload Failed");
    }

}

const startCameraBtn = document.getElementById("startCamera");
const captureBtn = document.getElementById("capture");

const camera = document.getElementById("camera");
const canvas = document.getElementById("canvas");
const capturedImage = document.getElementById("capturedImage");

const loading = document.getElementById("loading");
const results = document.getElementById("results");

let stream;

// Start Camera
startCameraBtn.onclick = async() => {

    try {

        stream = await navigator.mediaDevices.getUserMedia({
            video: true,
            audio: false
        });

        camera.srcObject = stream;

    } catch (err) {

        alert("Unable to access camera.");

        console.error(err);

    }

};

// Capture Photo
captureBtn.onclick = async() => {

    const ctx = canvas.getContext("2d");

    canvas.width = camera.videoWidth;
    canvas.height = camera.videoHeight;

    ctx.drawImage(camera, 0, 0);

    const imageData = canvas.toDataURL("image/jpeg");

    capturedImage.src = imageData;
    capturedImage.style.display = "block";

    await uploadToAWS(imageData);

};

// Loading Animation
function analyzeFace() {

    loading.style.display = "block";

    setTimeout(() => {

        loading.style.display = "none";

        showResults();

    }, 2500);

}

// Demo Results
function showResults() {

    results.style.display = "block";

    document.getElementById("emotion").innerHTML = "😊 Happy";
    document.getElementById("age").innerHTML = "22 - 30";
    document.getElementById("gender").innerHTML = "Male";
    document.getElementById("smile").innerHTML = "Yes";
    document.getElementById("glasses").innerHTML = "No";
    document.getElementById("beard").innerHTML = "Yes";
    document.getElementById("sunglasses").innerHTML = "No";
    document.getElementById("eyes").innerHTML = "Open";
    document.getElementById("brightness").innerHTML = "91%";
    document.getElementById("sharpness").innerHTML = "95%";
    document.getElementById("confidence").innerHTML = "99.92%";

    results.scrollIntoView({
        behavior: "smooth"
    });

}

function updateResults(data) {

    results.style.display = "block";

    document.getElementById("emotion").innerHTML = data.emotion;

    document.getElementById("age").innerHTML = data.age;

    document.getElementById("gender").innerHTML = data.gender;

    document.getElementById("smile").innerHTML = data.smile;

    document.getElementById("glasses").innerHTML = data.glasses;

    document.getElementById("beard").innerHTML = data.beard;

    document.getElementById("sunglasses").innerHTML = data.sunglasses;

    document.getElementById("eyes").innerHTML = data.eyesOpen;

    document.getElementById("brightness").innerHTML = data.brightness;

    document.getElementById("sharpness").innerHTML = data.sharpness;
document.getElementById("confidence").innerHTML = data.faceConfidence + "%"; 

}