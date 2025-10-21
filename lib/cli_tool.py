import argparse
import json
from pathlib import Path
from models import Task, User

STATE_PATH = Path(__file__).resolve().parent / "tasks_state.json"

def load_state():
    if STATE_PATH.exists():
        data = json.loads(STATE_PATH.read_text())
        users = {}
        for name, tasks in data.items():
            u = User(name)
            for t in tasks:
                task = Task(t["title"])
                if t.get("completed"):
                    task.completed = True
                u.tasks.append(task)
            users[name] = u
        return users
    return {}

def save_state(users):
    data = {}
    for name, u in users.items():
        data[name] = [{"title": t.title, "completed": t.completed} for t in u.tasks]
    STATE_PATH.write_text(json.dumps(data))

users = load_state()

def get_or_create_user(name):
    user = users.get(name)
    if not user:
        user = User(name)
        users[name] = user
    return user

def add_task_cmd(args):
    user = get_or_create_user(args.user)
    task = Task(args.title)
    user.add_task(task)
    save_state(users)

def complete_task_cmd(args):
    user = users.get(args.user)
    if not user:
        print("User not found.")
        return
    for task in user.tasks:
        if task.title == args.title:
            task.complete()
            save_state(users)
            return
    print("Task not found.")

def list_tasks_cmd(args):
    user = users.get(args.user)
    if not user:
        print("User not found.")
        return
    if not user.tasks:
        print("No tasks.")
        return
    for t in user.tasks:
        status = "done" if t.completed else "todo"
        print(f"{status}: {t.title}")

def build_parser():
    parser = argparse.ArgumentParser(description="Task Manager CLI")
    subparsers = parser.add_subparsers()

    add_parser = subparsers.add_parser("add-task", help="Add a new task for a user")
    add_parser.add_argument("user")
    add_parser.add_argument("title")
    add_parser.set_defaults(func=add_task_cmd)

    complete_parser = subparsers.add_parser("complete-task", help="Complete a task for a user")
    complete_parser.add_argument("user")
    complete_parser.add_argument("title")
    complete_parser.set_defaults(func=complete_task_cmd)

    list_parser = subparsers.add_parser("list-tasks", help="List tasks for a user")
    list_parser.add_argument("user")
    list_parser.set_defaults(func=list_tasks_cmd)

    return parser

if __name__ == "__main__":
    parser = build_parser()
    args = parser.parse_args()
    if hasattr(args, "func"):
        args.func(args)
    else:
        parser.print_help()
