import json
import boto3
import base64
import uuid
from datetime import datetime
from decimal import Decimal

s3 = boto3.client("s3")
rekognition = boto3.client("rekognition")
dynamodb = boto3.resource("dynamodb")

BUCKET_NAME = "emotion-detection"
TABLE_NAME = "emotion-detection"

table = dynamodb.Table(TABLE_NAME)


def dec(o):
    if isinstance(o, Decimal):
        return float(o)
    raise TypeError


def cors(code, body):
    return {
        "statusCode": code,
        "headers": {
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "*",
            "Access-Control-Allow-Methods": "OPTIONS,POST"
        },
        "body": json.dumps(body, default=dec)
    }


def lambda_handler(event, context):

    try:

        print("========== Lambda Started ==========")
        print(json.dumps(event))

        body = event.get("body")

        if isinstance(body, str):
            body = json.loads(body)

        if not body or "image" not in body:
            print("Image not found in request")
            return cors(400, {
                "status": "error",
                "message": "image missing"
            })

        img = body["image"]

        if "," in img:
            img = img.split(",", 1)[1]

        image_bytes = base64.b64decode(img)

        face_id = str(uuid.uuid4())

        ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")

        image_name = f"{ts}_{face_id}.jpg"

        key = f"uploads/{image_name}"

        print("Uploading image to S3...")

        s3.put_object(
            Bucket=BUCKET_NAME,
            Key=key,
            Body=image_bytes,
            ContentType="image/jpeg"
        )

        print("Image uploaded successfully.")

        print("Calling Rekognition...")

        resp = rekognition.detect_faces(
            Image={
                "S3Object": {
                    "Bucket": BUCKET_NAME,
                    "Name": key
                }
            },
            Attributes=["ALL"]
        )

        print("Rekognition Response:")
        print(resp)

        faces = resp.get("FaceDetails", [])

        if not faces:
            print("No Face Detected")
            return cors(200, {
                "status": "No Face Found"
            })

        face = faces[0]

        emotion = max(
            face["Emotions"],
            key=lambda x: x["Confidence"]
        )

        item = {
            "detectid": face_id,
            "ImageName": image_name,
            "S3Key": key,
            "UploadTime": datetime.utcnow().isoformat(),
            "AgeLow": face["AgeRange"]["Low"],
            "AgeHigh": face["AgeRange"]["High"],
            "Gender": face["Gender"]["Value"],
            "Emotion": emotion["Type"],
            "EmotionConfidence": Decimal(str(round(emotion["Confidence"], 2))),
            "Smile": face["Smile"]["Value"],
            "Beard": face["Beard"]["Value"],
            "Mustache": face["Mustache"]["Value"],
            "Eyeglasses": face["Eyeglasses"]["Value"],
            "Sunglasses": face["Sunglasses"]["Value"],
            "EyesOpen": face["EyesOpen"]["Value"],
            "MouthOpen": face["MouthOpen"]["Value"],
            "Brightness": Decimal(str(round(face["Quality"]["Brightness"], 2))),
            "Sharpness": Decimal(str(round(face["Quality"]["Sharpness"], 2))),
            "Pitch": Decimal(str(round(face["Pose"]["Pitch"], 2))),
            "Roll": Decimal(str(round(face["Pose"]["Roll"], 2))),
            "Yaw": Decimal(str(round(face["Pose"]["Yaw"], 2))),
            "FaceConfidence": Decimal(str(round(face["Confidence"], 2)))
        }

        print("========== DynamoDB Item ==========")
        print(item)

        print("Saving item to DynamoDB...")

        table.put_item(Item=item)

        print("Successfully stored in DynamoDB.")

        print("Returning Response...")

        return cors(200, {
            "status": "success",
            "detectid": face_id,
            "imageName": image_name,
            "age": f'{item["AgeLow"]}-{item["AgeHigh"]}',
            "gender": item["Gender"],
            "emotion": item["Emotion"],
            "emotionConfidence": item["EmotionConfidence"],
            "smile": "Yes" if item["Smile"] else "No",
            "beard": "Yes" if item["Beard"] else "No",
            "mustache": "Yes" if item["Mustache"] else "No",
            "glasses": "Yes" if item["Eyeglasses"] else "No",
            "sunglasses": "Yes" if item["Sunglasses"] else "No",
            "eyesOpen": "Yes" if item["EyesOpen"] else "No",
            "mouthOpen": "Yes" if item["MouthOpen"] else "No",
            "brightness": item["Brightness"],
            "sharpness": item["Sharpness"],
            "pose": {
                "pitch": item["Pitch"],
                "roll": item["Roll"],
                "yaw": item["Yaw"]
            },
            "faceConfidence": item["FaceConfidence"]
        })

    except Exception as e:

        print("========== ERROR ==========")
        print(str(e))

        return cors(500, {
            "status": "error",
            "message": str(e)
        })