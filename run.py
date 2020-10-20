"""
https://stackoverflow.com/questions/43184817/showing-video-on-the-entire-screen-using-opencv-and-tkiner
"""

from PIL import Image, ImageTk
import tkinter as tk
from tkinter import filedialog, messagebox
import argparse
from pathlib import Path
import config
import subprocess
import datetime
import cv2
import sys
import os


class Application:
    def __init__(self):
        self.output_path = str(Path().absolute()) + '/images'
        self.torch_image_path = ''

        self.vs = cv2.VideoCapture(0)
        self.current_image = None
        self.showing_torch_image = False

        self.root = tk.Tk()

        self.root.bind('<Escape>', self.destructor)
        self.root.bind('<Motion>', self.show_gui)
        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.attributes("-fullscreen", True)

        self.size = (self.root.winfo_screenwidth(),
                     self.root.winfo_screenheight())

        self.panel = tk.Label(self.root)
        self.panel.bind("<Button-1>", self.show_live_feed)
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

    def show_live_feed(self, arg):
        print(self.showing_torch_image)
        if self.showing_torch_image:
            self.showing_torch_image = False

    def hide_gui(self):
        self.options_btn.place_forget()
        self.snapshot_btn.place_forget()
        self.ml_button.place_forget()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            if self.showing_torch_image:
                img = cv2.imread(self.torch_image_path, 1)
                img = cv2.cvtColor(img, cv2.COLOR_BGR2RGBA)
                img = cv2.resize(img, self.size,
                                 interpolation=cv2.INTER_NEAREST)
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
        # Create image
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime(
            "%Y-%m-%d_%H-%M-%S"))
        p = os.path.join('/tmp/', filename)
        ok, frame = self.vs.read()
        if ok:
            snapshot = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA))
            snapshot.save(p, "PNG")

        if not os.path.isdir(config.YOLOv5_PATH) or not os.path.isfile(config.WEIGHTS):
            messagebox.showerror(
                title='Error', message='YOLOv5 path or weights are not properly set in config file.')
            return
        out_path = os.path.join(os.getcwd(), 'inference/output/')
        path_to_script = os.path.join(config.YOLOv5_PATH, 'detect.py')
        weights = ' --weights ' + config.WEIGHTS
        source = ' --source ' + p
        confidence = ' --conf-thres ' + str(config.CONFIDENCE_THRESHOLD)
        cmd = "python3.8 " + path_to_script + source + weights + confidence
        self.show_label('Sending image to ML algorithm. Please wait...')
        out = subprocess.check_output(
            cmd,
            stderr=subprocess.STDOUT,
            shell=True)
        self.torch_image_path = os.path.join(out_path, filename)
        self.show_label('Showing image. Press anywhere to resume to live feed.')
        self.showing_torch_image = True
        return

    def show_label(self, label):
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
