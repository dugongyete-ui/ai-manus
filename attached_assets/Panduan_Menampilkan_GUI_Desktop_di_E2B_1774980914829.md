# Panduan Menampilkan GUI Desktop di E2B.dev Sandbox

E2B.dev menyediakan lingkungan sandbox yang kuat untuk agen AI, termasuk kemampuan untuk menjalankan desktop virtual Linux dengan antarmuka pengguna grafis (GUI). Fitur ini memungkinkan agen AI untuk berinteraksi dengan aplikasi desktop seolah-olah mereka adalah pengguna manusia, membuka peluang baru untuk otomatisasi dan pengujian. Panduan ini akan menjelaskan bagaimana GUI desktop dapat ditampilkan dan diakses di sandbox E2B.dev.

## 1. Konsep Dasar E2B Desktop Sandbox

**E2B Desktop Sandbox** adalah lingkungan desktop virtual Linux yang aman dan terisolasi, dirancang khusus untuk agen AI. Lingkungan ini biasanya berbasis **Ubuntu 22.04** dan dilengkapi dengan desktop **XFCE** serta berbagai aplikasi umum. Tujuan utamanya adalah memungkinkan agen AI untuk "melihat", "memahami", dan "mengontrol" desktop virtual ini, mirip dengan cara manusia berinterinteraksi dengan komputer [1].

## 2. Mekanisme Tampilan GUI: Streaming VNC

Untuk menampilkan GUI desktop dari sandbox ke browser pengguna, E2B.dev menggunakan teknologi **Virtual Network Computing (VNC)**. Streaming VNC memungkinkan tampilan desktop virtual dikirimkan secara real-time ke browser pengguna melalui protokol yang aman. E2B.dev mengintegrasikan **noVNC**, sebuah klien VNC berbasis HTML5, untuk menyediakan akses berbasis browser yang mulus tanpa memerlukan instalasi klien VNC terpisah [1].

## 3. E2B Desktop SDK

**E2B Desktop SDK** adalah pustaka yang memungkinkan agen AI berinteraksi dengan desktop virtual. SDK ini menyediakan API untuk berbagai tindakan desktop, termasuk:

*   **Aksi Mouse**: `leftClick`, `rightClick`, `doubleClick`, `middleClick`, `moveMouse`, `drag`.
*   **Aksi Keyboard**: `write` (mengetik teks), `press` (menekan tombol tertentu).
*   **Pengguliran (Scrolling)**: `scroll` (menggulir ke atas atau ke bawah).
*   **Tangkapan Layar (Screenshots)**: `screenshot` (mengambil gambar dari keadaan desktop saat ini).
*   **Menjalankan Perintah Terminal**: `commands.run`.

Interaksi ini memungkinkan agen AI untuk mengotomatisasi tugas-tugas yang biasanya memerlukan interaksi visual dan manual [1].

## 4. Contoh Implementasi Python

Berikut adalah contoh kode Python dasar untuk membuat sandbox desktop dan memulai streaming VNC:

```python
from e2b_desktop import Sandbox

async def main():
    # Membuat sandbox desktop dengan resolusi 1024x720 dan timeout 5 menit
    sandbox = await Sandbox.create(
        resolution=[1024, 720],
        dpi=96,
        timeoutMs=300_000,
    )

    # Memulai streaming VNC untuk tampilan berbasis browser
    await sandbox.stream.start()
    stream_url = sandbox.stream.get_url()
    print('Lihat desktop di:', stream_url)

    # Di sini Anda dapat menambahkan logika agen AI untuk berinteraksi dengan desktop
    # Contoh: await sandbox.write('Hello, E2B Desktop!')
    # Contoh: await sandbox.leftClick(500, 300)

    # Setelah selesai, matikan sandbox
    await sandbox.kill()

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
```

Kode ini akan membuat sandbox, memulai streaming VNC, dan mencetak URL yang dapat Anda gunakan untuk melihat desktop virtual di browser Anda [1].

## 5. Template Desktop E2B

E2B.dev menyediakan template desktop yang sudah dikonfigurasi sebelumnya untuk memudahkan penggunaan. Template ini mencakup:

*   **Ubuntu 22.04** dengan lingkungan desktop XFCE.
*   **Streaming VNC** melalui noVNC untuk akses berbasis browser.
*   **Aplikasi Pra-instal**: LibreOffice, editor teks, pengelola file, dan utilitas umum lainnya.
*   **Alat Otomatisasi**: `xdotool` dan `scrot` untuk kontrol desktop secara terprogram [2].

## 6. Definisi Template

Definisi template melibatkan serangkaian langkah untuk menyiapkan lingkungan desktop. Ini termasuk:

*   **Instalasi Paket Sistem**: Menginstal paket-paket seperti `xserver-xorg`, `xfce4`, `x11vnc`, dan aplikasi lainnya yang diperlukan untuk lingkungan desktop.
*   **Setup noVNC dan websockify**: Mengkloning repositori noVNC dan websockify untuk mengaktifkan streaming VNC berbasis browser.
*   **Skrip Startup**: Mengatur skrip yang akan dijalankan saat sandbox dimulai untuk menginisialisasi desktop dan server VNC [2].

## 7. Skrip Startup (`start_command.sh`)

Skrip startup adalah komponen kunci yang menginisialisasi lingkungan GUI. Skrip ini biasanya melakukan hal berikut:

*   **Menginisialisasi Tampilan Virtual**: Menggunakan `Xvfb` (X Virtual Framebuffer) untuk membuat tampilan virtual tanpa memerlukan monitor fisik.
*   **Meluncurkan Sesi XFCE**: Memulai lingkungan desktop XFCE.
*   **Memulai Server VNC**: Menjalankan `x11vnc` untuk menyediakan akses VNC ke desktop.
*   **Mengekspos Desktop via noVNC**: Menggunakan `novnc_proxy` untuk mengekspos desktop melalui noVNC di port tertentu (misalnya, port 6080), sehingga dapat diakses melalui browser [2].

## 8. Proses Build Template

Karena instalasi lingkungan desktop melibatkan banyak paket, proses build template untuk desktop sandbox mungkin memerlukan alokasi sumber daya yang lebih tinggi (CPU dan memori) dan waktu yang lebih lama. E2B.dev memungkinkan Anda untuk mengonfigurasi alokasi sumber daya ini saat membangun template [2].

Dengan mengikuti panduan ini, Anda dapat memahami dan mengimplementasikan GUI desktop di sandbox E2B.dev untuk kebutuhan agen AI Anda.

## Referensi

[1] E2B. Computer use - Documentation. [https://e2b.dev/docs/use-cases/computer-use](https://e2b.dev/docs/use-cases/computer-use)
[2] E2B. Sandbox with Ubuntu Desktop and VNC access - Documentation. [https://e2b.dev/docs/template/examples/desktop](https://e2b.dev/docs/template/examples/desktop)
