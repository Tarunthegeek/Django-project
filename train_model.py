"""Train and persist the logistic regression model artifact."""
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

import django


def main() -> None:
    django.setup()
    from api.ml import train_and_save_model

    artifact = train_and_save_model()
    print(f'Model saved to {artifact}')


if __name__ == '__main__':
    main()
