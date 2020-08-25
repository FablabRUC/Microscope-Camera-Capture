"""
https://stackoverflow.com/questions/43184817/showing-video-on-the-entire-screen-using-opencv-and-tkiner
"""

from PIL import Image, ImageTk
import tkinter as tk
import argparse
import datetime
import cv2
import os


class Application:
    def __init__(self, output_path="./"):
        self.vs = cv2.VideoCapture(0)
        self.output_path = output_path
        self.current_image = None

        self.root = tk.Tk()
        # self.root.title("Microscope")

        self.root.protocol('WM_DELETE_WINDOW', self.destructor)
        self.root.attributes("-fullscreen", True)

        self.size = (self.root.winfo_screenwidth(),
                     self.root.winfo_screenheight() - 30)

        self.panel = tk.Label(self.root)
        self.panel.pack(fill='both', expand=True)

        self.btn = tk.Button(self.root, text="Snapshot!",
                             command=self.take_snapshot)
        self.btn.pack(fill='both', expand=True)

        self.video_loop()

    def video_loop(self):
        ok, frame = self.vs.read()
        if ok:
            cv2image = cv2.cvtColor(frame, cv2.COLOR_BGR2RGBA)
            cv2image = cv2.resize(cv2image, self.size,
                                  interpolation=cv2.INTER_NEAREST)
            # .resize(self.size, resample=Image.NEAREST)  # convert image for PIL
            self.current_image = Image.fromarray(cv2image)
            self.panel.imgtk = ImageTk.PhotoImage(image=self.current_image)
            self.panel.config(image=self.panel.imgtk)
            self.root.after(1, self.video_loop)

    def take_snapshot(self):
        ts = datetime.datetime.now()  # grab the current timestamp
        filename = "{}.jpg".format(ts.strftime(
            "%Y-%m-%d_%H-%M-%S"))
        p = os.path.join(self.output_path, filename)
        self.current_image.save(p, "PNG")
        self.show_label(filename)

    def show_label(self, filename):
        print("[INFO] saved {}".format(filename))
        self.info_label = tk.Label(self.root,
                                   text="Saved {}".format(filename),
                                   fg="white",
                                   bg="darkgrey",
                                   font="Helvetica 28 bold")
        self.info_label.place(relx=0.0, rely=0.0, anchor='nw')
        self.root.after(5000, self.info_label.destroy)

    def destructor(self):
        self.root.destroy()
        self.vs.release()
        cv2.destroyAllWindows()


ap = argparse.ArgumentParser()
ap.add_argument("-o", "--output", default="./images",
                help="path to output directory to store snapshots (default: current folder")
args = vars(ap.parse_args())

# start the app
print("[INFO] starting...")
pba = Application(args["output"])
pba.root.mainloop()
