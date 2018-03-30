from joblib import Parallel, delayed
import multiprocessing
import pano as panoramic
import time
import shutil
import cv2
import os
import traceback

stiching_dir = os.getcwd()
movies_dir = os.path.join(stiching_dir, "movies")

files_content = "movies/examples/{example_name}/frame1.jpg\n" + \
    "movies/examples/{example_name}/frame2.jpg\n" + \
    "movies/examples/{example_name}/frame3.jpg\n"


def filter_example(element):
    try:
        if len(element) > 0 and len(os.listdir(element)) == 4:
            # return element[0] == 'e'
            return True
        return False
    except NotADirectoryError:
        return False


def create_examples(movie, movie_dir, examples_dir):
    count_frame = 0
    count_example = 0
    frame_count_name = 1
    flag = 0

    # directory = os.getcwd()
    example_dir = os.path.join(examples_dir, f"e{count_example}_m{movie}")
    example_name = f"e{count_example}_m{movie}"
    os.mkdir(example_dir)
    frames_dir = os.path.join(
        movie_dir, "frames/frame{}.jpg".format(count_frame))
    # os.chdir()
    # os.listdir(os.getcwd())

    frame = cv2.imread(frames_dir)

    while frame is not None:
        # Le frame
        frames_dir = os.path.join(
            movie_dir, "frames/frame{}.jpg".format(count_frame))
        frame = cv2.imread(frames_dir)

        # Muda para diretório movies/movieX/exemploX
        # os.chdir(example_dir)
        frame_name = os.path.join(
            example_dir,
            f"e{count_example}_m{movie}_f{frame_count_name}.jpg"
        )
        example_name = f"e{count_example}_m{movie}"
        # Salva frame na pasta
        cv2.imwrite(frame_name, frame)

        # Volta para diretório movies/movieX
        # os.chdir(directory)

        # Caso já tenham 3 exemplos,
        # 1 - Cria arquivo txt
        # 2 - Cria outra pasta de exemplos
        # 3 - Aumenta contator de exemplos
        if len(os.listdir(example_dir)) > 2:
            # os.chdir(example_dir)
            files_path = os.path.join(example_dir, "files.txt")
            with open(files_path, "w") as file:
                file.write(files_content.format(example_name=example_name))
            # os.chdir(directory)
            count_example += 1
            example_dir = os.path.join(
                examples_dir, f"e{count_example}_m{movie}")
            example_name = f"e{count_example}_m{movie}"
            os.mkdir(example_dir)
            flag = True

        # Aumenta contator de frames
        if flag:
            frame_count_name = 1
            count_frame += 30
            flag = False
        else:
            count_frame += 20
            frame_count_name += 1

        # # Medida de precaucao
        # if count_example > 100:
        #     break


def get_frames(video_name, movie_dir):
    video_name = os.path.join(movie_dir, video_name)
    vidcap = cv2.VideoCapture(video_name + ".mp4")
    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        file_name = os.path.join(movie_dir, "frames/frame{}.jpg")
        success, image = vidcap.read()
        # Savar imagem na pasta 'frames'
        # e retornar ao diretório movieX
        cv2.imwrite(file_name.format(count), image)
        # exit if Escape is hit
        if cv2.waitKey(10) == 27:
            break
        count += 1


def generate_frames_and_examples(movie):
    # Gera lista de filmes
    # movies = os.listdir(movies_dir)
    # os.chdir(movies_dir)

    # Para cada filme
    # 1- Entra na pasta do filme
    # 2- Se nao tem pasta de frames,
    # cria pasta com frames
    # 3- Cria exemplos
    # for movie in movies:
    movie_dir = os.path.join(movies_dir, movie)

    if 'frames' not in os.listdir(movie_dir):
        os.mkdir(os.path.join(movie_dir, 'frames'))
        get_frames(movie, movie_dir)

    if 'examples' not in os.listdir(movies_dir):
        os.mkdir(os.path.join(movies_dir, 'examples'))

    examples_dir = os.path.join(movies_dir, 'examples')
    create_examples(movie, movie_dir, examples_dir)
    shutil.rmtree(os.path.join(movie_dir, 'frames'))


def movie_genesis():
    # Vá para diretório de filmes
    os.chdir(movies_dir)
    movies = os.listdir(movies_dir)

    # STICHING PART
    # 1 - filtra os examplos para utilizar apenas
    # aqueles que possuem todos os arquivos
    # 2 -62118
    for movie in movies:
        os.chdir(os.path.join(movies_dir, movie))
        examples = os.listdir()
        examples_filtered = list(filter(filter_example, examples))
        os.chdir(stiching_dir)
        for example in examples_filtered:
            stichImages(movie, example)


def stichImages(count, movie, example):
    files_path = "movies/{movie}/{example}/files.txt".format(
        movie=movie, example=example)
    folder_path = "movies/{movie}/{example}/panoramic.jpg".format(
        movie=movie, example=example)
    print("{}----------- STARTING STICHING -----------".format(count))
    try:
        panoramic.start_stiching(files_path, folder_path)
    except Exception:
        traceback.print_exc()
        print(example)
        shutil.rmtree(
            "movies/{movie}/{example}".format(movie=movie, example=example))
    finally:
        print("{}----------- FINISHING STICHING -----------".format(count))


if __name__ == '__main__':
    start = time.time()
    num_cores = multiprocessing.cpu_count()
    # Parallel(n_jobs=num_cores, timeout=30)(generate_frames_and_examples)

    # generate_frames_and_examples()
    # movie_genesis()

    movies = os.listdir(movies_dir)
    # for movie in movies:
        # movie_dir = os.path.join(movies_dir, movie)

    #     if 'frames' not in os.listdir(movies_dir):
    #         os.mkdir(os.path.join(movie_dir, 'frames'))
    #         get_frames(movie, movie_dir)

    #     create_examples(movie, movie_dir)
    #     shutil.rmtree(os.path.join(movie_dir, 'frames'))

    results = Parallel(n_jobs=num_cores)(
        delayed(generate_frames_and_examples)(movie) for movie in movies)

    # os.chdir(movies_dir)
    movies = os.listdir(movies_dir)

    # STICHING PART
    # 1 - filtra os examplos para utilizar apenas
    # aqueles que possuem todos os arquivos
    # 2 -62118
    # count = 0
    # for movie in movies:
    #     os.chdir(os.path.join(movies_dir, movie))
    #     examples = os.listdir()
    #     examples_filtered = list(filter(filter_example, examples))
    #     os.chdir(stiching_dir)
    #     count = count + 4
    #     try:
    #         results = Parallel(n_jobs=num_cores, verbose=11)(delayed(stichImages)(
    #             count, movie, example) for example in examples_filtered)
    #     except:
    #         print("ERROR ao gerar imagem")
    #         pass

    # stop = time.time()
    # print("minutes: {}".format(int((stop - start) / 60)))
    # print("seconds: {}".format((stop - start) % 60))


# def deadline(timeout, *args):
#     def decorate(f):
#         def handler(signum, frame):
#             raise TimedOutExc()

#         def new_f(*args):

#             signal.signal(signal.SIGALRM, handler)
#             signal.alarm(timeout)
#             return f(*args)
#             signa.alarm(0)

#         new_f.__name__ = f.__name__
#         return new_f
#     return decorate


# def timeOut(time, func):
#
