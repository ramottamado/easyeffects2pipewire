from itertools import pairwise


def create_links(data: list[str]) -> list[dict[str, str]]:
    """
    Create links & plugin orders settings.

    :param data: list of plugins
    :type data: list[str]
    :return: links settings
    :rtype: list[dict[str, str]]
    """

    data_l = [plugin for plugin in data if not plugin.endswith("_r")]
    data_r = [plugin for plugin in data if not plugin.endswith("_l")]

    links_channel_left = [
        {
            "output": f"{plugin[0] + '_l:Out' if plugin[0].startswith('convolver') else plugin[0] + ':out_l'}",
            "input": f"{plugin[1] + '_l:In' if plugin[1].startswith('convolver') else plugin[1] + ':in_l'}",
        }
        for plugin in pairwise(data_l)
    ]

    links_channel_right = [
        {
            "output": f"{plugin[0] + '_r:Out' if plugin[0].startswith('convolver') else plugin[0] + ':out_r'}",
            "input": f"{plugin[1] + '_r:In' if plugin[1].startswith('convolver') else plugin[1] + ':in_r'}",
        }
        for plugin in pairwise(data_r)
    ]

    return links_channel_left + links_channel_right


def create_inputs(data: list[str]) -> list[str]:
    """
    Create inputs settings.

    :param data: list of plugins
    :type data: list[str]
    :return: inputs settings
    :rtype: list[str]
    """

    if data[0].startswith("convolver"):
        return [
            f"{data[0]}_l:In",
            f"{data[0]}_r:In",
        ]

    return [
        f"{data[0]}:in_l",
        f"{data[0]}:in_r",
    ]


def create_outputs(data: list[str]) -> list[str]:
    """
    Create outputs settings.

    :param data: list of plugins
    :type data: list[str]
    :return: outputs settings
    :rtype: list[str]
    """

    if data[-1].startswith("convolver"):
        return [
            f"{data[-1]}_l:Out",
            f"{data[-1]}_r:Out",
        ]

    return [
        f"{data[-1]}:out_l",
        f"{data[-1]}:out_r",
    ]
