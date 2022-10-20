from PIL import Image
from glob import glob
import os
from tqdm import tqdm 


SAVE_FOLDER = "training_data"
def augment_images(folder_path: str, resize: bool, img_count: int = 0) -> int:
    save_path = os.path.join(os.getcwd(), SAVE_FOLDER)
    if not os.path.exists(save_path):
        os.makedirs(save_path)
    for path in tqdm(glob(f"{folder_path}/*/*.jpeg")):
        if os.path.exists(path) and os.path.isfile(path):
            img = Image.open(path).convert("RGB")
            if resize:
                img = img.resize((256, 256))
            for angle in [90, 180, 270, 360]:
                im_rotated = img.rotate(angle, expand=True)
                file_path = os.path.normpath(os.path.join(save_path, f"train_img_{img_count}.jpeg"))
                im_rotated.save(file_path)
                img_count += 1
        else:
           print(f"Path: {path} not a file or doesn't exist")
    return img_count


def main() -> None:
    count = augment_images(os.path.join(os.getcwd(), 'training_data_256'), resize=False)
    augment_images(os.path.join(os.getcwd(), 'training_data_512'), resize=True, img_count=count)

    

if __name__ == "__main__":
    main()
