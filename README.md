# MotionEye CSI Camera Fix using v4l2loopback + FFmpeg

This repository documents how to use a **Raspberry Pi CSI camera (v1.3 / OV5647)** with **MotionEye** on **Raspberry Pi OS Bullseye (32-bit)** by bridging the camera output to a **v4l2loopback dummy device**.

MotionEye often fails to show CSI camera video because it expects a **V4L2 camera device**, while Raspberry Pi CSI cameras are handled differently by the kernel and camera stack. This setup works around that limitation cleanly and reliably.

---

## 🧩 Problem

- MotionEye does **not display CSI camera video**
- Camera appears as `vc.ril.camera`
- `/dev/video0` exists but MotionEye cannot use it directly
- Selecting MMAL or V4L2 shows no video
- MotionEye requires a standard **V4L2-compatible device**

---

## 💡 Solution Overview

We solve this by:
1. Creating a **dummy V4L2 camera** using `v4l2loopback`
2. Using **FFmpeg** to forward the real CSI camera (`/dev/video0`) into the dummy device (`/dev/video1`)
3. Running everything automatically at **system boot** using systemd services
4. Configuring MotionEye to use `/dev/video1`

---

## 🛠 Requirements

- Raspberry Pi (Zero / Zero 2 / 3 / 4)
- CSI Camera (OV5647 / v1.3)
- Raspberry Pi OS Bullseye (32-bit)
- MotionEye installed
- Required packages:

```bash
sudo apt install ffmpeg v4l2loopback-dkms v4l-utils
````

---

## 📷 Camera Devices

| Device        | Description                          |
| ------------- | ------------------------------------ |
| `/dev/video0` | Real CSI camera                      |
| `DummyCam`    | Dummy camera created by v4l2loopback |

---

## 🔧 Systemd Services

### 1️⃣ v4l2loopback.service

Creates the dummy V4L2 camera at boot.

```ini
[Unit]
Description=Load v4l2loopback dummy camera
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/sbin/modprobe v4l2loopback video_nr=1 card_label=DummyCam exclusive_caps=1
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

**What this service does:**

* Loads the `v4l2loopback` kernel module
* Creates `/dev/video1`
* Labels it as `DummyCam`
* Runs once at boot

---

### 2️⃣ ffmpeg-bridge.service

Bridges the real CSI camera to the dummy camera.

```ini
[Unit]
Description=FFmpeg bridge from /dev/video0 to /dev/video1
After=v4l2loopback.service
Requires=v4l2loopback.service

[Service]
ExecStart=/usr/bin/ffmpeg -f v4l2 -i /dev/video0 -r 30 -f v4l2 /dev/video1
Restart=always
RestartSec=3

[Install]
WantedBy=multi-user.target
```

**What this service does:**

* Reads video from `/dev/video0`
* Converts it into a standard V4L2 stream
* Forwards it to `/dev/video1`
* Forces **30 FPS**
* Automatically restarts on failure

---

## 🚀 Enable & Start Services

```bash
sudo systemctl daemon-reload
sudo systemctl enable v4l2loopback.service
sudo systemctl enable ffmpeg-bridge.service
sudo systemctl start v4l2loopback.service
sudo systemctl start ffmpeg-bridge.service
```

After reboot, both services will start automatically.

---

## 🎥 MotionEye Configuration

1. Open MotionEye Web UI
2. Add **Local V4L2 Camera**
3. Set:

   * **Camera Device:** `/dev/video1`
   * **Camera Name:** DummyCam
4. Save

🎉 MotionEye will now show the CSI camera feed correctly.

---

## 🧪 Debugging

List video devices:

```bash
ls /dev/video*
```

List camera formats:

```bash
v4l2-ctl --list-devices
```

View FFmpeg logs:

```bash
journalctl -u ffmpeg-bridge.service -f
```

Check service status:

```bash
systemctl status v4l2loopback.service
systemctl status ffmpeg-bridge.service
```

---

## ✅ Result

* CSI camera works reliably with MotionEye
* Stable **30 FPS**
* No `device busy` errors
* Fully automatic on boot
* Works on low-power boards like Raspberry Pi Zero
