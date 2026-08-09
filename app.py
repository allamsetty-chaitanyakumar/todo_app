from flask import Flask, render_template, request, redirect
import sqlite3

app = Flask(__name__)


def get_db_connection():
    conn = sqlite3.connect("todo.db")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db_connection()

    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            task TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)

    conn.commit()
    conn.close()


def add_completed_column():
    conn = get_db_connection()

    try:
        conn.execute(
            "ALTER TABLE tasks ADD COLUMN completed INTEGER DEFAULT 0"
        )
        conn.commit()
    except sqlite3.OperationalError:
        pass

    conn.close()


@app.route("/", methods=["GET", "POST"])
def home():

    conn = get_db_connection()

    if request.method == "POST":
        task = request.form["task"]

        if task:
            conn.execute(
                "INSERT INTO tasks (task) VALUES (?)",
                (task,)
            )
            conn.commit()

    tasks = conn.execute(
        "SELECT * FROM tasks"
    ).fetchall()

    conn.close()

    return render_template("index.html", tasks=tasks)


@app.route("/delete/<int:id>")
def delete(id):

    conn = get_db_connection()

    conn.execute(
        "DELETE FROM tasks WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")


@app.route("/complete/<int:id>")
def complete(id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET completed = 1 WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/incomplete/<int:id>")
def incomplete(id):

    conn = get_db_connection()

    conn.execute(
        "UPDATE tasks SET completed = 0 WHERE id = ?",
        (id,)
    )

    conn.commit()
    conn.close()

    return redirect("/")

@app.route("/edit/<int:id>", methods=["GET", "POST"])
def edit(id):

    conn = get_db_connection()

    if request.method == "POST":
        task = request.form["task"]

        conn.execute(
            "UPDATE tasks SET task = ? WHERE id = ?",
            (task, id)
        )

        conn.commit()
        conn.close()

        return redirect("/")

    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (id,)
    ).fetchone()

    conn.close()

    return render_template("edit.html", task=task)


if __name__ == "__main__":
    init_db()
    add_completed_column()
    app.run(debug=True)