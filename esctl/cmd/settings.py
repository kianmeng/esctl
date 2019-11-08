from esctl.commands import EsctlShowOne, EsctlCommandSetting
from esctl.utils import Color
from esctl.exceptions import SettingNotFoundError


class ClusterSettingsGet(EsctlCommandSetting):
    """Get a setting value."""

    def retrieve_setting(self, setting_name, persistency):
        setting = self.cluster_settings.get(setting_name, persistency=persistency)

        if setting.value is not None:
            if setting.persistency == "defaults":
                output = "{} ({})".format(
                    setting.value, Color.colorize("default", Color.ITALIC)
                )
            else:
                output = setting.value

            return output

        else:
            raise SettingNotFoundError(
                "{} does not exists in {} cluster settings.".format(
                    Color.colorize(setting.name, Color.ITALIC),
                    Color.colorize(persistency, Color.ITALIC),
                )
            )

    def take_action(self, parsed_args):
        persistency = "persistent" if parsed_args.persistent else "transient"
        self.log.debug("Persistency is " + persistency)

        try:
            print(self.retrieve_setting(parsed_args.setting, persistency))
        except SettingNotFoundError as error:
            self.log.error(error)


class ClusterSettingsList(EsctlShowOne):
    """(EXPERIMENTAL) List available settings."""

    def take_action(self, parsed_args):
        default_settings = {}
        settings_list = self.cluster_settings.list().get("defaults")

        for (setting_name, setting_value) in settings_list.items():
            if type(setting_value).__name__ == "list":
                if len(setting_value) > 0:
                    setting_value = ",\n".join(setting_value)
                else:
                    setting_value = "[]"

            default_settings[setting_name] = setting_value

        return (tuple(default_settings.keys()), tuple(default_settings.values()))


class ClusterSettingsReset(EsctlCommandSetting):
    """Reset a setting value."""

    def take_action(self, parsed_args):
        persistency = "persistent" if parsed_args.persistent else "transient"
        self.log.debug("Persistency is " + persistency)
        print(
            "Resetting {} to its default value".format(
                Color.colorize(parsed_args.setting, Color.ITALIC)
            )
        )
        print(
            self.cluster_settings.set(
                parsed_args.setting, None, persistency=persistency
            )
        )


class ClusterSettingsSet(EsctlCommandSetting):
    """Set a setting value."""

    def take_action(self, parsed_args):
        persistency = "persistent" if parsed_args.persistent else "transient"
        self.log.debug("Persistency is " + persistency)

        print(
            "Changing {} to {}".format(
                Color.colorize(parsed_args.setting, Color.ITALIC),
                Color.colorize(parsed_args.value, Color.ITALIC),
            )
        )

        print(
            self.cluster_settings.set(
                parsed_args.setting, parsed_args.value, persistency=persistency
            )
        )

    def get_parser(self, prog_name):
        parser = super().get_parser(prog_name)
        parser.add_argument("value", metavar="<value>", help=("Setting value"))
        return parser
