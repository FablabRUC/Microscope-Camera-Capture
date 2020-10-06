"""
https://stackoverflow.com/questions/43184817/showing-video-on-the-entire-screen-using-opencv-and-tkiner
"""

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog
import argparse
from pathlib import Path
import subprocess
import datetime
import cv2
import sys
import os


class Application:
    def __init__(self):
        self.output_path = str(Path().absolute()) + '/images'

        self.vs = cv2.VideoCapture(0)
        self.current_image = None

        self.root = tk.Tk()

        self.root.bind('<Escape>', self.destructor)
        self.root.bind('<Motion>', self.show_gui)
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.attributes("-fullscreen", True)

        self.size = (self.root.winfo_screenwidth(),
                     self.root.winfo_screenheight())

        self.panel = tk.Label(self.root)
        if sys.platform == 'linux':
            self.root.config(cursor='none')
        self.panel.pack(fill='both', expand=True)

        self.snapshot_btn = tk.Button(self.root, text="Snapshot!",
                                      command=self.take_snapshot,
                                      width=8, height=8)

        self.options_btn = tk.Button(self.root, text="Options",
                                     command=self.set_save_directory,
                                     width=8, height=8)

        self.ml_button = tk.Button(self.root, text="ML",
                                     command=self.send_to_torch,
                                     width=8, height=8)

        self.showing_torch_image = True
                                     
        self.video_btn = tk.Button(self.root, text="Video",
                                   command=self.record_video,
                                   width=8, height=8)
        self.info_label = tk.Label(self.root)
        self.video_loop()

    def show_gui(self, arg):
        self.snapshot_btn.place(relx=0.0, rely=1.0, anchor='sw')
        self.options_btn.place(relx=0.0, rely=0.0, anchor='nw')
        self.ml_button.place(relx=1.0, rely=1.0, anchor='se')
        # self.video_btn.place(relx=1.0, rely=1.0, anchor='se')
        self.root.after(5000, self.hide_gui)

    def hide_gui(self):
        self.options_btn.place_forget()
        self.snapshot_btn.place_forget()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            if self.showing_torch_image:
                img = cv2.imread('/Users/frederikjuutilainen/Programming/FabLab/microscope_gui/inference/output/2020-10-06_11-53-08.jpg', 1) 
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                self.current_image = Image.fromarray(img)
            else:
                cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
                cv2image = cv2.resize(cv2image, self.size,
                                    interpolation=cv2.INTER_NEAREST)
                self.current_image = Image.fromarray(cv2image)
            self.panel.imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.config(image=self.panel.imgtk)
            self.root.after(1, self.video_loop)

    def take_snapshot(self):
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime(
            "%Y-%m-%d_%H-%M-%S"))
        p = os.path.join(self.output_path, filename)
        ok, frame = self.vs.read()
        if ok:
            snapshot = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
            snapshot.save(p, "PNG")
            self.show_label("[INFO] saved {}".format(filename))

    def record_video(self):
        return

    def set_save_directory(self):
        self.output_path = filedialog.askdirectory(
            initialdir=self.output_path, title="Set output path")
        return

    def send_to_torch(self):
        print('Sending to torch')
        # Create image
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime(
            "%Y-%m-%d_%H-%M-%S"))
        p = os.path.join('/tmp/', filename)
        ok, frame = self.vs.read()
        if ok:
            snapshot = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
            snapshot.save(p, "PNG")
        
        # Send to YOLOv5
        yolo_path = '/Users/frederikjuutilainen/Programming/FabLab/yolov5/'
        out_path = os.path.join(yolo_path,'inference/output/')
        path_to_script = os.path.join(yolo_path, 'detect.py')
        weights = ' --weights /Users/frederikjuutilainen/Programming/FabLab/yolov5/weights/blood.pt'
        source = ' --source ' + p
        cmd = "python3.8 " + path_to_script + source + weights
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True)
        self.show_torch_image(os.path.join(out_path,filename))
        return

    def show_torch_image(self, path):
        print(path)

    def show_label(self, label):
        print(label)
        self.info_label.destroy()
        self.info_label = tk.Label(self.root,
                                   text=label,
                                   fg="white",
                                   bg="darkgrey",
                                   font="Helvetica 28 bold")
        self.info_label.place(relx=0.0, rely=0.0, anchor='nw')
        self.root.after(5000, self.info_label.destroy)

    def destructor(self, arg):
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


print("[INFO] starting...")
pba = Application()
pba.root.mainloop()
