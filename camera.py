import cv2
import numpy as np
import traffic_light_classifier as tlc
from PIL import Image
from datetime import datetime
from led import RGBLED


CAMERA_WIDTH = 640
CAMERA_HEIGHT = 480


class CAMERA(object):
    __instance = None
    __init_flag = False
    def __new__(cls):
        if cls.__instance == None:
            cls.__instance = object.__new__(cls)
            return cls.__instance
        else:
            return cls.__instance
        
    def __init__(self):
        if self.__init_flag == False:
            self.cap = cv2.VideoCapture(0)
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAMERA_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAMERA_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, 15)
            self.model = self.load_model()
            self.is_running = True
            self.rgbled = RGBLED()
        else:
            pass
        
    def load_model(self):
        """Load Traffic Light Classifier model, returns a Model instance."""
        model = tlc.Model()
        model.compile(show_analysis=False)
        return model

    def process_image(self, image, show_probabilities=False, show_analysis=False):
        """Process an image, Return predicted label."""
        image_np = np.array(image)  # Convert PIL image to NumPy array
        label_predicted = self.model.predict(image_np, show_probabilities=show_probabilities, show_analysis=show_analysis)
        return label_predicted

    def display_result(self, label, frame):
        """Display the predicted label in the top right corner"""
        if (label[0]):
            self.rgbled.green_off()
            self.rgbled.red_on()
        elif (label[1]):
            self.rgbled.green_off()
            self.rgbled.red_off()
        else:
            self.rgbled.green_on()
            self.rgbled.red_off()
        cv2.imshow('Traffic Light Classification', frame)
        


    def close_camera(self):
        self.is_running = False
        return

    def capture(self):
        while self.is_running:
            ret, frame = self.cap.read()
            if not ret:
                continue

            image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
            label_predicted = self.process_image(image, show_probabilities=False, show_analysis=False)
            self.display_result(label_predicted, frame)
            

            k = cv2.waitKey(1)
            if k == 27:  # ESC to exit
                self.is_running = False
            elif k == ord('s'):  # 's' to save image
                timestamp = datetime.now().isoformat()
                cv2.imwrite(f'{timestamp}.jpg', frame)
            
            ret, buffer = cv2.imencode('.jpeg', frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: image/jpeg\r\n\r\n' + frame + b'\r\n')
            

        self.cap.release()
        cv2.destroyAllWindows()



