# portfoliohub/services/builders/snapshot_builder.py


class SnapshotBuilder:

    @staticmethod
    def build(snapshot):

        return {
            "profile_snapshot_id":
                snapshot.profile_snapshot_id,

            "title":
                snapshot.title,

            "target_role":
                snapshot.target_role,

            "description":
                snapshot.description,
        }
