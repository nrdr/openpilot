import ctypes, platform, unittest
from dataclasses import replace
from unittest.mock import patch
import numpy as np
from tinygrad import Device, Tensor, dtypes
from tinygrad.helpers import Context, Target
from tinygrad.renderer.cstyle import ClangRenderer
from tinygrad.uop.ops import KernelInfo, Ops, ProgramInfo, UOp

class TestQCOM(unittest.TestCase):
  def test_program_cache_keeps_image_signature(self):
    from tinygrad.runtime import ops_qcom as qcom
    def program(dtype, width):
      param = UOp.param(0, dtype, 512)
      param = param.replace(arg=replace(param.arg, image=(512 // (width * 4), width)))
      return UOp(Ops.PROGRAM, src=(UOp(Ops.SINK, arg=KernelInfo(name="same_binary")), UOp(Ops.LINEAR, src=(param,)),
                                  UOp(Ops.SOURCE, arg=""), UOp(Ops.BINARY, arg=b"identical kernel")),
                 arg=ProgramInfo(global_size=(1, 1, 1), local_size=(1, 1, 1), globals=(0,), outs=(0,), ins=(),
                                 target=Target(device="QCOM")))
    programs = [program(dtype, width) for dtype, width in ((dtypes.half, 16), (dtypes.float, 16), (dtypes.half, 32))]
    with patch.object(qcom, "_qcom_program_cache", {}), patch.object(qcom, "QCOMProgramData") as build:
      build.return_value.image = b"compiled"
      for prg in programs:
        first = qcom.qcom_build_program(None, prg, ("QCOM",))
        self.assertIs(first, qcom.qcom_build_program(None, prg, ("QCOM",)))
      self.assertEqual(build.call_count, 3)

  @unittest.skipUnless(Device.DEFAULT == "QCOM", "needs QCOM")
  def test_same_binary_different_image_dtypes(self):
    # Upstream regression: image2d_t/read_imagef share a binary but not a texture format.
    with Context(IMAGE=1):
      x = Tensor(np.random.default_rng(0).standard_normal(512).astype(np.float32)).realize()
      for dtype in (dtypes.half, dtypes.float):
        b = Tensor(np.random.default_rng(1).standard_normal(512).astype(np.float32)).cast(dtype).contiguous().realize()
        np.testing.assert_allclose((x + b.float()).numpy(), x.numpy() + b.numpy().astype(np.float32), rtol=1e-3, atol=1e-3)

  # although part of the QCOM runtime, this tests flushing the CPU's dcache
  @unittest.skipUnless(isinstance(Device["CPU"].renderer, ClangRenderer) and platform.machine().lower() in {"arm64", "aarch64"},
                       "dcache_flush's inline asm needs ClangRenderer, and runs on arm64")
  def test_dcache_flush(self):
    from tinygrad.runtime.ops_qcom import dcache_flush
    buf = (ctypes.c_uint8 * 64)()
    dcache_flush().fxn(buf, 0)

if __name__ == '__main__':
  unittest.main()
