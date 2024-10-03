import csv

from django.db.models import QuerySet


def export_to_csv(queryset: QuerySet) -> None:
    """Export PlayerLevel queryset to csv file."""

    with open('player_levels.csv', 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['Player ID', 'Level', 'Is Completed', 'Prize'])

        for player_level in queryset:
            prize_title = None
            player_level_prize = player_level.received_prize
            if player_level_prize:
                prize_title = player_level_prize.prize.title

            writer.writerow([
                player_level.player.player_id,
                player_level.level.title,
                player_level.is_completed,
                prize_title or ''
            ])
