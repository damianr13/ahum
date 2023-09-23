import typer

from src import firestore
from src.processing import SongProcessor
from src.schemas.song import SongWithLanguage

app = typer.Typer()


@app.command()
def read_dictionary_file(dictionary_file: str):
    print("Reading dictionary file...")
    with open(f"data/dictionaries/{dictionary_file}", "r", encoding="latin-1") as f:
        words = f.read().splitlines()

    print(words[:10])


@app.command()
def publish_processed_song(firestore_id: str):
    print("Publishing processed song...")
    db = firestore.init_firestore()

    song: SongWithLanguage = SongWithLanguage(
        **db.collection("songs").document(firestore_id).get().to_dict()
    )
    processor = (
        SongProcessor(song)
        .create_line_reordering_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .create_word_selection_task()
        .mask_words_according_to_tasks()
    )

    processed_song = processor.get_processed_song()

    db.collection("songs").document(firestore_id).set(processed_song.model_dump())


if __name__ == "__main__":
    app()
