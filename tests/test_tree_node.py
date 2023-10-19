
import unittest
from tree_node import TreeNode


class TestTreeNode(unittest.TestCase):
    def setUp(self):
        # Create an instance of the TreeNode class as root node for testing
        self.root_node = TreeNode("test_node", is_file=False, parent_node=None)

    def test_add_and_remove_child(self):
        # Test case for add_child method and remove child method
        child_node = TreeNode("child", is_file=False, parent_node=self.root_node)
        self.root_node.add_child(child_node)
        self.assertIn(child_node, self.root_node.children)
        self.assertTrue(self.root_node.remove_child("child"))
        self.assertNotIn(child_node, self.root_node.children)

    def test_remove_all_children(self):
        # Test case for remove_all_children method
        child1 = TreeNode("child1", is_file=False, parent_node=self.root_node)
        child2 = TreeNode("child2", is_file=True, parent_node=self.root_node)
        self.root_node.add_child(child1)
        self.root_node.add_child(child2)
        self.root_node.remove_all_children()
        self.assertEqual(len(self.root_node.children), 0)

    def test_get_child_by_name(self):
        # Test case for get_child_by_name method
        child1 = TreeNode("child1", is_file=False, parent_node=self.root_node)
        child2 = TreeNode("child2", is_file=False, parent_node=self.root_node)
        self.root_node.add_child(child1)
        self.root_node.add_child(child2)
        found_child = self.root_node.get_child_by_name("child1")
        self.assertEqual(found_child, child1)
        not_found_child = self.root_node.get_child_by_name("non_existent_child")
        self.assertIsNone(not_found_child)

if __name__ == "__main__":
    unittest.main()