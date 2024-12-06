import cv2
import os
from datetime import datetime
from app.logger import get_logger
from app.database import add_or_update_dog

logger = get_logger(__name__)

IMAGES_CORE = "static/images"

def save_image(category, obj_id, frame, bbox, timestamp):    
    base_dir = f"{IMAGES_CORE}/{category}/{obj_id}"
    os.makedirs(base_dir, exist_ok=True)
    image_path = f"{base_dir}/{timestamp}.jpg"

    x, y, w, h = [int(v) for v in bbox.to_tuple()]
    cropped = frame[y:y + h, x:x + w]
    cv2.imwrite(image_path, cropped)
    return image_path

def check_if_recently_saved(category, obj_id, timestamp, cooldown=10):
    base_dir = f"{IMAGES_CORE}/{category}/{obj_id}"
    if os.path.isdir(base_dir):
        files = [f for f in os.listdir(base_dir) if f.endswith(".jpg")]
        if files:
            latest_file = max(files, key=lambda f: datetime.strptime(f.split('.')[0], "%Y-%m-%d_%H-%M-%S"))
            latest_timestamp = datetime.strptime(latest_file.split('.')[0], "%Y-%m-%d_%H-%M-%S")
            
            current_time = datetime.strptime(timestamp, "%Y-%m-%d_%H-%M-%S")
            # logger.info(f"current time - latest_timestamp = {(current_time - latest_timestamp).total_seconds()}")
            if (current_time - latest_timestamp).total_seconds() < cooldown:
                return True
    return False

def export(category_pl, obj_id, frame, bbox):
    now = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    if not check_if_recently_saved(category_pl, obj_id, now):
        image_path = save_image(category_pl, obj_id, frame, bbox, now)
        logger.info(f"Saved image to {category_pl}, obj_id = {obj_id} // {now}")

        if "dog" in category_pl:
            add_or_update_dog(obj_id, image_path, now, now)
