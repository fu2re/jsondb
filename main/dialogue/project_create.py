# coding: utf-8
import os
from distutils import dir_util
from data.projects_manager import projectManager
from project_add_dialog import ProjectAddDialog


def ensure_dir(f):
    d = os.path.dirname(f)
    if not os.path.exists(d):
        os.makedirs(d)

class ProjectCreateDialog(ProjectAddDialog):
    """Диалог для создания проекта"""

    def __init__(self, parent=None):
	ProjectAddDialog.__init__(self, parent)
        self.setWindowTitle(u'Создание проекта')

    def _addProject(self):        
        pth = u'%s' % self.edtPath.text()
        name = u'%s' % self.edtName.text()
        dst = os.path.join(pth, name)
        ensure_dir(dst)
        os.makedirs(os.path.join(dst, 'html'))
        os.makedirs(os.path.join(dst, 'balance'))
        dir_util.copy_tree('initial', dst)
        projectManager.addProject(name, dst)
        self.accept()
