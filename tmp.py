from apps.aiModule.utils.util_model import get_initial_decide
from datetime import datetime
from django.utils import timezone


def main():
    li = get_initial_decide(3)
    print(f'response -> {li}')


if __name__ == "__main__":
    main()
