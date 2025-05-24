from flask import Flask, render_template_string, redirect, request, jsonify
import subprocess
import pyautogui
import ctypes

# Disable failsafe to allow full touchpad area
pyautogui.FAILSAFE = False
# Virtual key codes for media control\ nVK_MEDIA_PLAY_PAUSE = 0xB3
VK_MEDIA_NEXT_TRACK  = 0xB0
VK_MEDIA_PREV_TRACK  = 0xB1
VK_VOLUME_UP         = 0xAF
VK_VOLUME_DOWN       = 0xAE

app = Flask(__name__)

def send_media_key(vk_code):
    ctypes.windll.user32.keybd_event(vk_code, 0, 0, 0)
    ctypes.windll.user32.keybd_event(vk_code, 0, 2, 0)

# --- HTML Templates ---
HOME_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Пульт ПК</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #1e1e1e; color: #fff; text-align: center; margin: 0; padding: 2em; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #007bff; color: #fff; font-size: 1.2em; text-decoration: none; border-radius: 0.5em; width: 90%; max-width: 300px; }
  </style>
</head>
<body>
  <h1>Пульт ПК</h1>
  <a class='button' href='/launch/browser'>Запустити браузер</a>
  <a class='button' href='/sites'>Сайти</a>
  <a class='button' href='/power'>Живлення</a>
  <a class='button' href='/displays'>Дисплеї</a>
  <a class='button' href='/multimedia'>Мультимедіа</a>
  <a class='button' href='/mousepad'>Миша</a>
</body>
</html>
"""

SITES_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Сайти</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #111; color: #fff; text-align: center; margin: 0; padding: 2em; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #28a745; color: #fff; font-size: 1.2em; text-decoration: none; border-radius: 0.5em; width: 90%; max-width: 300px; }
  </style>
</head>
<body>
  <h1>Сайти</h1>
  <a class='button' href='/'>← Назад</a>
  <a class='button' href='/launch/youtube'>YouTube</a>
  <a class='button' href='/launch/simpsonsua'>SimpsonsUA</a>
  <a class='button' href='/launch/uakino'>UaKino</a>
</body>
</html>
"""

POWER_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Живлення</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #111; color: #fff; text-align: center; margin: 0; padding: 2em; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #ffc107; color: #000; font-size: 1.2em; text-decoration: none; border-radius: 0.5em; width: 90%; max-width: 300px; }
    .danger { background: #dc3545; color: #fff; }
  </style>
</head>
<body>
  <h1>Живлення</h1>
  <a class='button' href='/'>← Назад</a>
  <a class='button danger' href='/launch/shutdown'>Вимкнути комп’ютер</a>
  <a class='button danger' href='/launch/restart'>Перезапустити комп’ютер</a>
  <a class='button' href='/launch/sleep'>Увійти в режим сну</a>
  <a class='button' onclick="alert('Щоб вийти з режиму сну – скористайся Wake-on-LAN або мишкою/клавіатурою')">Вийти з режиму сну</a>
</body>
</html>
"""

DISPLAYS_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Дисплеї</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #111; color: #fff; text-align: center; margin: 0; padding: 2em; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #17a2b8; color: #fff; font-size: 1.2em; text-decoration: none; border-radius: 0.5em; width: 90%; max-width: 300px; }
  </style>
</head>
<body>
  <h1>Дисплеї</h1>
  <a class='button' href='/'>← Назад</a>
  <a class='button' href='/launch/display_pc'>Дисплей ПК</a>
  <a class='button' href='/launch/display_tv'>Дисплей ТВ</a>
  <a class='button' href='/launch/display_extend'>Розширити</a>
</body>
</html>
"""

MULTIMEDIA_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Мультимедіа</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #111; color: #fff; text-align: center; margin: 0; padding: 2em; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #6c757d; color: #fff; font-size: 1.2em; text-decoration: none; border-radius: .5em; width: 90%; max-width: 300px; }
  </style>
</head>
<body>
  <h1>Мультимедіа</h1>
  <a class='button' href='/media/playpause'>Плей/Пауза</a>
  <a class='button' href='/media/volumeup'>Звук +</a>
  <a class='button' href='/media/volumedown'>Звук -</a>
  <a class='button' href='/media/next'>Наступне</a>
  <a class='button' href='/media/prev'>Попереднє</a>
  <a class='button' href='/'>← Назад</a>
</body>
</html>
"""

MOUSEPAD_HTML = """
<!DOCTYPE html>
<html lang='uk'>
<head>
  <meta charset='UTF-8'>
  <title>Тачпад</title>
  <meta name='viewport' content='width=device-width, initial-scale=1.0'>
  <style>
    body { font-family: sans-serif; background: #000; color: #fff; text-align: center; margin: 0; padding: 0; overflow: hidden; }
    .button { display: block; margin: 1em auto; padding: 1em; background: #28a745; color: #fff; font-size: 1.2em; text-decoration: none; border-radius: 0.5em; width: 90%; max-width: 300px; }
    #touchpad { margin: 1em auto; background: #222; width: 90%; max-width: 360px; height: 360px; border: 2px solid #555; border-radius: 8px; touch-action: none; }
    #keyboard { display: none; width: 90%; max-width: 360px; padding: 1em; font-size: 1.2em; border-radius: 0.5em; margin-top: 1em; }
  </style>
</head>
<body>
  <div id='touchpad'></div>
  <textarea id='keyboard' placeholder='Введіть текст...'></textarea>
  <a class='button' href='/'>← Назад</a>
  <script>
    const tp = document.getElementById('touchpad');
    let isDown = false, lastX = 0, lastY = 0, queued = false, dxTotal = 0, dyTotal = 0;
    let lastTapTime = 0;

    tp.addEventListener('pointerdown', e => {
      isDown = true; lastX = e.clientX; lastY = e.clientY;
      const now = Date.now();
      if(now - lastTapTime < 300) {
        const kb = document.getElementById('keyboard'); kb.style.display = 'block'; kb.focus();
      }
      lastTapTime = now;
      tp.setPointerCapture(e.pointerId);
    });

    tp.addEventListener('pointermove', e => {
      if(!isDown) return;
      const dx = e.clientX - lastX, dy = e.clientY - lastY;
      dxTotal += dx; dyTotal += dy;
      lastX = e.clientX; lastY = e.clientY;
      if(!queued) {
        queued = true;
        setTimeout(() => {
          fetch('/mouse/move', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({dx:Math.round(dxTotal*3), dy:Math.round(dyTotal*3)})});
          dxTotal=0; dyTotal=0; queued=false;
        }, 16);
      }
    });

    tp.addEventListener('pointerup', e => {
      isDown = false; tp.releasePointerCapture(e.pointerId);
      fetch('/mouse/click', {method:'POST'});
    });

    document.getElementById('keyboard').addEventListener('input', e => {
      fetch('/type', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify({text:e.target.value})});
      e.target.value='';
    });
  </script>
</body>
</html>
"""

# --- Routes ---
@app.route('/')
def home(): return render_template_string(HOME_HTML)

@app.route('/sites')
def sites(): return render_template_string(SITES_HTML)

@app.route('/power')
def power(): return render_template_string(POWER_HTML)

@app.route('/displays')
def displays(): return render_template_string(DISPLAYS_HTML)

@app.route('/multimedia')
def multimedia(): return render_template_string(MULTIMEDIA_HTML)

@app.route('/mousepad')
def mousepad(): return render_template_string(MOUSEPAD_HTML)

@app.route('/mouse/move', methods=['POST'])
def mouse_move():
    data=request.get_json(); pyautogui.moveRel(data.get('dx',0), data.get('dy',0)); return jsonify(success=True)

@app.route('/mouse/click', methods=['POST'])
def mouse_click():pyautogui.click();return jsonify(success=True)

@app.route('/type', methods=['POST'])
def type_text():
    text=request.get_json().get('text',''); pyautogui.write(text); return jsonify(success=True)

@app.route('/media/<action>')
def media_control(action):
    keys={'playpause':VK_MEDIA_PLAY_PAUSE,'next':VK_MEDIA_NEXT_TRACK,'prev':VK_MEDIA_PREV_TRACK,'volumeup':VK_VOLUME_UP,'volumedown':VK_VOLUME_DOWN}
    send_media_key(keys.get(action,0))
    return redirect('/multimedia')

@app.route('/launch/<action>')
def launch(action):
    edge=r"C:\\Program Files (x86)\\Microsoft\\Edge\\Application\\msedge.exe"
    apps={
      'browser':edge,'youtube':[edge,'https://www.youtube.com'], 'simpsonsua':[edge,'https://simpsonsua.tv/'],
      'uakino':[edge,'https://uakino.me/'], 'shutdown':'shutdown /s /t 0', 'restart':'shutdown /r /t 0',
      'sleep':'rundll32.exe powrprof.dll,SetSuspendState 0,1,0',
      'display_pc':'C:\\Windows\\System32\\DisplaySwitch.exe /internal',
      'display_tv':'C:\\Windows\\System32\\DisplaySwitch.exe /external',
      'display_extend':'C:\\Windows\\System32\\DisplaySwitch.exe /extend'
    }
    cmd=apps.get(action)
    if cmd:
        try:
            if isinstance(cmd,list):subprocess.Popen(cmd)
            elif action in ['shutdown','restart','sleep'] or action.startswith('display_'):subprocess.call(cmd,shell=True)
            else:subprocess.Popen([cmd])
        except Exception as e:
            return f"<h2>Помилка: {e}</h2>"
    return redirect('/')

if __name__=='__main__':
    app.run(host='0.0.0.0', port=8080)
