'''
office access control system
https://github.com/ageitgey/face_recognition/blob/master/README_Simplified_Chinese.md
https://github.com/ageitgey/face_recognition/blob/master/examples/facerec_from_webcam_faster.py
https://github.com/wwj718/cv_note/tree/master/face_detect
    https://github.com/wwj718/cv_note/blob/master/face_detect/facerec_from_webcam_faster_print.py
'''
import face_recognition
import cv2
import numpy as np
import subprocess

# This is a demo of running face recognition on live video from your webcam. It's a little more complicated than the
# other example, but it includes some basic performance tweaks to make things run a lot faster:
#   1. Process each video frame at 1/4 resolution (though still display it at full resolution)
#   2. Only detect faces in every other frame of video.

# PLEASE NOTE: This example requires OpenCV (the `cv2` library) to be installed only to read from your webcam.
# OpenCV is *not* required to use the face_recognition library. It's only required if you want to run this
# specific demo. If you have trouble installing it, try any of the other demos that don't require it instead.

# Get a reference to webcam #0 (the default one)
video_capture = cv2.VideoCapture(0)

# Load a sample picture and learn how to recognize it.
# obama_image = face_recognition.load_image_file("obama.jpg")
# obama_face_encoding = face_recognition.face_encodings(obama_image)[0]

# Load a second sample picture and learn how to recognize it.
# biden_image = face_recognition.load_image_file("biden.jpg")
# biden_face_encoding = face_recognition.face_encodings(biden_image)[0]

# python3 ../camera/read_from_webcam_screenshot.py
my_image = face_recognition.load_image_file("test.jpg")
my_face_encoding = face_recognition.face_encodings(my_image)[0]

# Create arrays of known face encodings and their names
known_face_encodings = [
    # obama_face_encoding, biden_face_encoding, my_face_encoding
    my_face_encoding
]
known_face_names = ["myself"]

# Initialize some variables
face_locations = []
face_encodings = []
face_names = []


def main():
    process_this_frame = True
    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = small_frame[:, :, ::-1]

        # Only process every other frame of video to save time
        if process_this_frame:
            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(
                rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(
                    known_face_encodings, face_encoding,tolerance=0.3)
                name = "Unknown"

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(
                    known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                face_names.append(name)

        process_this_frame = not process_this_frame

        # Display the results
        for (top, right, bottom, left), name in zip(face_locations,
                                                    face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            print(name)
            # print(name, (left, top), (right, bottom))
            subprocess.call(f"codelab-message-pub -t adapter/extensions/data -c {name}", shell=True)

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


try:
    main()
except KeyboardInterrupt:
    pass
# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()
