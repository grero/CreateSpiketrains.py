import CreateSpiketrains
import CreateSpiketrains.create_spiketrains as create_spiketrains
import matplotlib
import os
import pytest
from urllib.request import urlopen
import tempfile
import hashlib
import scipy.io as mio
import shutil

def download_file(fname):
    _file = urlopen("http://cortex.nus.edu.sg/testdata/array01/channel001/%s" % (fname,))
    with open(fname, "wb") as output:
        output.write(_file.read())

@pytest.mark.order2
def test_pick_lines(qtbot):
    dd = tempfile.mkdtemp()
    cwd = os.getcwd()
    os.chdir(dd)
    #download data
    download_file("hmmsort.mat")
    download_file("spike_templates.hdf5")
    window = create_spiketrains.ViewWidget()
    window.show()
    window.select_waveforms()
    qtbot.addWidget(window)
    #simulate a pick event
    event1 = matplotlib.backend_bases.PickEvent("A pick", window.figure.canvas, [],window.figure.axes[0].lines[0])
    window.pick_event(event1)
    event2 = matplotlib.backend_bases.PickEvent("A pick", window.figure.canvas, [],window.figure.axes[0].lines[1])
    window.pick_event(event2)
    window.save_spiketrains(notify=False)
    #check that we got what we expected
    q1 =  mio.loadmat("cell01/unit.mat")
    hh1 = hashlib.sha1(q1["timestamps"].tostring()).hexdigest()
    assert hh1 == '8093ffc2459eb613bcc10f65e34b0c47568e22ae'
    q2 =  mio.loadmat("cell02/unit.mat")
    hh2 = hashlib.sha1(q2["timestamps"].tostring()).hexdigest()
    assert hh2 == '03de5a1a19919c3ede7030d760aebcf671379c7f'
    os.unlink("cell01/unit.mat")
    os.unlink("cell02/unit.mat")
    os.rmdir("cell01")
    os.rmdir("cell02")

    #unpick
    window.pick_event(event1)
    window.pick_event(event2)
    window.counter = 0

    #merge waveforms
    mevent = matplotlib.backend_bases.MouseEvent("Mouse event", window.figure.canvas, 0,0,button=matplotlib.backend_bases.MouseButton.LEFT, key="shift")
    event1 = matplotlib.backend_bases.PickEvent("A pick", window.figure.canvas, mevent,window.figure.axes[0].lines[0])
    window.pick_event(event1)
    event2 = matplotlib.backend_bases.PickEvent("A pick", window.figure.canvas, mevent,window.figure.axes[0].lines[1])
    window.pick_event(event2)
    assert len(window.merged_lines) == 2

    window.save_spiketrains(notify=False)
    assert os.path.isfile("cell01/unit.mat")
    assert os.path.isfile("cell02/unit.mat") == False
    os.unlink("cell01/unit.mat")
    os.rmdir("cell01")

    #auto-discovery
    os.mkdir("channel001")
    os.mkdir("channel002")
    shutil.copyfile("hmmsort.mat", "channel001/hmmsort.mat")
    shutil.copyfile("spike_templates.hdf5", "channel001/spike_templates.hdf5")
    shutil.copyfile("hmmsort.mat", "channel002/hmmsort.mat")
    shutil.copyfile("spike_templates.hdf5", "channel002/spike_templates.hdf5")
    os.unlink("hmmsort.mat")
    os.unlink("spike_templates.hdf5")
    window.find_files()
    assert len(window.picked_lines) == 0
    assert len(window.merged_lines) == 0

    assert window.filelist.count() == 2
    assert window.filelist.itemText(0) == "./channel001/hmmsort.mat"
    assert window.filelist.itemText(1) == "./channel002/hmmsort.mat"

    #cleanup
    for ch in ['channel001','channel002']:
        for f in ['hmmsort.mat','spike_templates.hdf5']:
            os.unlink(os.path.join(ch,f))
        os.rmdir(ch)
    os.chdir(cwd)
    os.rmdir(dd)
