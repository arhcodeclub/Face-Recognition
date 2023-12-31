#==========================================================================#
# Required libraries                                                       #
# To install run:                                                          #
# ~$ pip install face_recognition opencv-python numpy playsound            #
#==========================================================================#

import face_recognition
import cv2
import numpy as np
import time
import playsound

import config as cfg

#Webcam
video_capture = cv2.VideoCapture(0)



# Create arrays from config of known face encodings and their names
known_face_names = cfg.known_face_names
known_face_music = cfg.known_face_music
known_face_encodings = []

timeout = 0
# /8 because deltatime is prolly incorect
hold_time = cfg.hold_duration/8

# Images
for imagestr in cfg.known_face_images:
    image = face_recognition.load_image_file(imagestr)
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)




# Initialize some variables
face_locations = []
face_encodings = []
face_names = []
process_this_frame = True

confidence = 1

deltatime = 0

while True:
    start = time.time()


    # Grab a single frame of video
    ret, frame = video_capture.read()

    # Only process every other frame of video to save time
    if process_this_frame:
        confidence = 1

        # Resize frame of video to 1/4 size for faster face recognition processing
        small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

        # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
        rgb_small_frame = np.ascontiguousarray(small_frame[:, :, ::-1])
        
        # Find all the faces and face encodings in the current frame of video
        face_locations = face_recognition.face_locations(rgb_small_frame)
        face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

        face_names = []
        face_index = -1

        hold_time += deltatime

        for face_encoding in face_encodings:
            # See if the face is a match for the known face(s)
            matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
            name = "Unknown"

            # # If a match was found in known_face_encodings, just use the first one.
            # if True in matches:
            #     first_match_index = matches.index(True)
            #     name = known_face_names[first_match_index]

            # Or instead, use the known face with the smallest distance to the new face
            face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
            best_match_index = np.argmin(face_distances)
            if matches[best_match_index]:
                name = known_face_names[best_match_index]
                confidence = face_distances[best_match_index]
                if confidence < cfg.face_treshold:
                    #2 deltatime times because it is always being removed 
                    hold_time -= 2*deltatime

                    if hold_time < 0:
                        # Set the face index for the audio player to see
                        face_index = best_match_index

            face_names.append(name)

    process_this_frame = not process_this_frame

    font = cv2.FONT_HERSHEY_DUPLEX

    # Display the results
    for (top, right, bottom, left), name in zip(face_locations, face_names):
        # Scale back up face locations since the frame we detected in was scaled to 1/4 size
        top *= 4
        right *= 4
        bottom *= 4
        left *= 4

        # Draw a box around the face
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

        # Draw a label with a name below the face
        cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
        cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)

    #Draw debug variables
    color = (0,0,255)
    if (confidence < cfg.face_treshold):
        color = (0,255,0)
    cv2.putText(frame,"Confidence: " + str(round((1-confidence)*100))+"% / "+str((1-cfg.face_treshold)*100)+"%",(0,25),font,1.0,color,1)
    cv2.putText(frame,"hold: " + str(round(hold_time*4,2)),(0,50),font,1.0,(255,255,255),1)
    cv2.putText(frame,"cooldown: " + str(round(timeout,2)),(0,75),font,1.0,(255,255,255),1)


    # Display the resulting image
    cv2.imshow('Video', frame)

    #if face is detected
    if face_index > -1 and timeout <= 0:
        timeout = cfg.timeout_time
        # /8 because deltatime is prolly incorect
        hold_time = cfg.hold_duration/8
        playsound.playsound(known_face_music[face_index])

    timeout -= deltatime
    if timeout <= 0:
        timeout = 0
    if hold_time > cfg.hold_duration/8:
        hold_time = cfg.hold_duration/8

    # Hit 'q' on the keyboard to quit!
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

    deltatime = time.time() - start


# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()