from tagmerad import tag, config
from .batch import Batch
from jeanpaulstart import tags
from jeanpaulstart import parser
from jeanpaulstart.constants import *


def from_folders(folders):
    """
    Loads all the batches in given folders
    :param folders: A list of folders
    :return: A list of successfully loaded batches
    """
    batches = list()

    for filepath in parser.from_folders(folders):
        batch = Batch(filepath=filepath)
        if batch.load_status == OK:
            batches.append(batch)

    return batches


def from_folders_for_user(batch_directories, username, tags_filepath, elasticsearch_url=None, elasticsearch_index=None):
    """
    Loads all the batches in given folders, with matching tags for given tags file and username
    :param batch_directories: A list of folders
    :param tags_filepath: The filepath to the tags definition file
    :param elasticsearch_url: The url of elasticsearch database
    :param username: The username
    :return: A list of successfully loaded batches
    """
    user_batches = list()
    batches = from_folders(batch_directories)
    if elasticsearch_url:
        config.set_persistence("ElasticSearch", {"url": elasticsearch_url, 'index_prefix': elasticsearch_index})
        user_tags = tag.by_user(username)
        user_tags = set(tag.parse_groups(user_tags))
    else:
        user_tags = set(tags.load_by_user(tags_filepath, username))

    for batch_ in batches:
        if not user_tags.isdisjoint(batch_.tags):
            # check tags options
            for batch_option in reversed(batch_.options):
                if user_tags.isdisjoint(batch_option.tags):
                    batch_.options.remove(batch_option)
            user_batches.append(batch_)

    return user_batches
