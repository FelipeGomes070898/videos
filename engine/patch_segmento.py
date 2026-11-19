import subprocess, sys
from multiprocessing import Pool
import main as M
A, B = int(sys.argv[1]), int(sys.argv[2])   # quadros [A, B) a re-renderizar
def run(out1080, out4k):
    cmd = ['ffmpeg','-y','-v','error','-f','rawvideo','-pix_fmt','rgb24','-s','1080x1920','-r','30','-i','-',
           '-filter_complex','[0:v]split=2[a][b];[b]scale=2160:3840:flags=lanczos[c]',
           '-map','[a]','-c:v','libx264','-preset','veryfast','-crf','18','-pix_fmt','yuv420p',out1080,
           '-map','[c]','-c:v','libx264','-preset','veryfast','-crf','21','-pix_fmt','yuv420p',out4k]
    ff = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    with Pool(2) as p:
        for fr in p.imap(M.frame, range(A, B), chunksize=3):
            ff.stdin.write(fr)
    ff.stdin.close(); ff.wait()
import os
run(os.path.join(M.OUT_DIR, 'seg_1080.mp4'), os.path.join(M.OUT_DIR, 'seg_4k.mp4'))
