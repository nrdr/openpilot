"""Recover interrupted object builds without sweeping the checkout or shared cache."""
import os
import stat

from SCons.CacheDir import CacheDir
from SCons.Errors import BuildError
from SCons.Node.FS import File


def _empty_regular_file(path):
  try:
    info = os.lstat(path)
  except FileNotFoundError:
    return False
  return info.st_size == 0 and stat.S_ISREG(info.st_mode)


def _object(node):
  return isinstance(node, File) and node.name.endswith(('.o', '.os')) and node.has_builder()


class ObjectCache(CacheDir):
  def retrieve(self, node):
    if self.is_enabled() and _object(node) and _empty_regular_file(self.cachepath(node)[1]):
      return False  # A miss: run the normal compiler, never unlink from a shared cache.
    return super().retrieve(node)

  def push(self, node):
    if _object(node) and _empty_regular_file(node.abspath):
      raise BuildError(node=node, errstr=f'compiler produced an empty object: {node}')
    return super().push(node)


def recover_object_targets(nodes):
  for node in nodes:
    if _object(node):
      # Cover independent submodule environments as well as clones of the root env.
      env = node.get_build_env()
      env['CACHEDIR_CLASS'] = ObjectCache
      if _empty_regular_file(node.abspath):
        env.AlwaysBuild(node)  # An otherwise up-to-date truncated target must be replaced.
