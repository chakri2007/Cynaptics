from keras.utils import to_categorical
from tensorflow.keras.utils import load_img
from keras.models import Sequential
from keras.applications import MobileNetV2, ResNet152, VGG16, EfficientNetB0, InceptionV3
from keras.layers import Dense, Conv2D, Dropout, Flatten, MaxPooling2D, BatchNormalization, GlobalAveragePooling2D
import os
from sklearn.preprocessing import LabelEncoder
import pandas as pd
import numpy as np
from tqdm.notebook import tqdm
from google.colab import drive
drive.mount('/content/drive')

def createdataframe(dir):
    image_paths = []
    labels = []
    for label in os.listdir(dir):
        for imagename in os.listdir(os.path.join(dir, label)):
            image_paths.append(os.path.join(dir, label, imagename))
            labels.append(label)
        print(label, "completed")
    return image_paths, labels

def extract_features(images):
    features = []
    for image in tqdm(images):
        img = load_img(image, target_size=(236, 236))
        img = np.array(img)
        features.append(img)
    features = np.array(features)
    features = features.reshape(features.shape[0], 236, 236, 3)  # Reshape all images in one go
    return features

TRAIN_DIR = "/content/drive/MyDrive/Data/Train"

train = pd.DataFrame()
train['image'], train['label'] = createdataframe(TRAIN_DIR)

train_features = extract_features(train['image'])

x_train = train_features / 255.0

le = LabelEncoder()
le.fit(train['label'])
y_train = le.transform(train['label'])
y_train = to_categorical(y_train, num_classes=2)

model = Sequential()
# Convolutional layers
model.add(Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=(236, 236, 3)))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(256, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(512, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Conv2D(1024, kernel_size=(3, 3), activation='relu'))
model.add(MaxPooling2D(pool_size=(2, 2)))

model.add(Flatten())
model.add(Dense(1024, activation='relu'))
model.add(Dropout(0.3))
model.add(Dense(2048, activation='relu'))
model.add(Dense(2, activation='softmax'))

model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
model.fit(x=x_train, y=y_train, batch_size=25, epochs=50)

model.save('/content/drive/MyDrive/ml_results/AivsReal_tained.keras')

# TESTING THE MODEL
TEST_DIR = "/content/drive/MyDrive/Data/Test"
image_paths = []
predictions = []

for image_id in os.listdir(TEST_DIR):
    image_path = os.path.join(TEST_DIR, image_id)
    image_paths.append(image_path)
features = extract_features(image_paths)
features = features / 255.0
predictions_prob = model.predict(features)
predicted_classes = np.argmax(predictions_prob, axis=1)
predicted_labels = le.inverse_transform(predicted_classes)
results = pd.DataFrame({
    'Id': [os.path.splitext(os.path.basename(path))[0] for path in image_paths],  # Strip '.jpg' extension
    'Label': predicted_labels
})
results.to_csv('/content/drive/MyDrive/ml_results/RESULTS_final.csv', index=False)

print(f"Predictions saved to RESULTS_final.csv")



results.to_csv('/content/drive/MyDrive/ml_results/RESULTS_final.csv', index=False)
print("Predictions saved to RESULTS.csv")
