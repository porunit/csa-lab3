import contextlib
import io
import logging
import os
import tempfile



import computer.machine
import pytest
import language.translator


@pytest.mark.golden_test("golden/*.yml")
def test_program(golden, caplog):
    with tempfile.TemporaryDirectory() as tmpdirname:
        code = os.path.join(tmpdirname, "code")
        inputs = os.path.join(tmpdirname, "inputs")
        target = os.path.join(tmpdirname, "target")
        with open(code, "w", encoding="utf-8") as f:
            f.write(golden["in_source"])
        with open(inputs, "w", encoding="utf-8") as f:
            f.write(golden["in_stdin"])

        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            language.translator.main(code, target)
            print("============================================================")
            computer.machine.main(target, inputs)

        with open(target, encoding="utf-8") as f:
            machine_code = f.read()

        assert machine_code == golden.out["out_code"]
        assert stdout.getvalue()[:-1].replace('\x00','') == golden.out["out_stdout"]