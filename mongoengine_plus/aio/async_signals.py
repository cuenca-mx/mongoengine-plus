from mongoengine.signals import Namespace

async_signals = Namespace()

pre_save = async_signals.signal("pre_save")
post_save = async_signals.signal("post_save")
