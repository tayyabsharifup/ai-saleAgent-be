from apps.aiModule.utils.util_model import get_initial_decide
from datetime import datetime
from django.utils import timezone


def main(num: int):
    li = get_initial_decide(num)
    print(f'response -> {li}')


if __name__ == "__main__":
    main(num)
