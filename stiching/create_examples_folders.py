import cv2
import os
import get_frames

stiching_dir = "/home/felipe/Documents/deep_learning/stiching"
movies_dir = "/home/felipe/Documents/deep_learning/stiching/movies"


def create_examples():
    count_frame = 0
    count_example = 0
    frame_name = 1
    flag = 0

    directory = os.getcwd()
    example_dir = "exemplo{}".format(count_example)

    os.mkdir(example_dir)
    # os.chdir()
    # os.listdir(os.getcwd())

    frame = cv2.imread("frame{}.jpg".format(count_frame))

    while frame is not None:
        # Le frame
        frame = cv2.imread("frame{}.jpg".format(count_frame))

        # Muda para diretório movies/movieX/exemploX
        os.chdir(os.path.join(directory, example_dir))

        # Salva frame na pasta
        cv2.imwrite("frame{}.jpg".format(frame_name), frame)

        # Volta para diretório movies/movieX
        os.chdir(directory)

        # Caso já tenham 3 exemplos,
        # cria outra pasta de exemplos
        # e aumenta contator de exemplos
        if len(os.listdir(os.path.join(directory, example_dir))) > 2:
            count_example += 1
            example_dir = "exemplo{}".format(count_example)
            os.mkdir(example_dir)
            flag = True

        # Aumenta contator de frames
        if flag:
            frame_name = 1
            count_frame += 20
            flag = False
        else:
            count_frame += 10
            frame_name += 1

        # Medida de precaucao
        if count_example > 100:
            break


def get_frames(video_name, parental_dir):
    vidcap = cv2.VideoCapture(video_name + ".mp4")
    success, image = vidcap.read()
    count = 0
    success = True
    while success:
        success, image = vidcap.read()
        # Savar imagem na pasta 'frames'
        # e retornar ao diretório movieX
        os.chdir('frames')
        cv2.imwrite("frame{}.jpg".format(count), image)
        os.chdir(parental_dir)
        # exit if Escape is hit
        if cv2.waitKey(10) == 27:
            break
        count += 1


def movie_genesis():
    # Gera lista de filmes
    movies = os.listdir(movies_dir)

    # Para cada filme
    # 1- Entra na pasta do filme
    # 2- Se nao tem pasta de frames,
    # cria pasta com frames
    # 3- Cria exemplos
    for movie in movies:
        os.chdir(movie)

        if 'frames' not in os.listdir(os.getcwd()):
            os.mkdir('frames')
            get_frames(movie, os.getcwd())

        create_examples()

        os.chdir(movies_dir)


if __name__ == '__main__':
    movie_genesis()
