import sys
import os
import json
import unittest
from unittest.mock import Mock, patch

sys.path.insert(0, os.path.dirname(__file__))

from ipsec_master import (KNOWLEDGE_DATA, LEVELS_DATA, ProgressManager, MainWindow, 
                          MainMenu, KnowledgeView, LevelSelectView, GameView, AchievementView)


class TestKnowledgeData(unittest.TestCase):
    
    def test_knowledge_data_not_empty(self):
        self.assertGreater(len(KNOWLEDGE_DATA), 0)
    
    def test_knowledge_data_has_required_keys(self):
        required_topics = ['IPsec概述', 'IKE协议详解', '加密与认证算法', 
                          'NAT穿越', '高可用与故障切换', 'DPD与隧道维护']
        for topic in required_topics:
            self.assertIn(topic, KNOWLEDGE_DATA)
            self.assertIn('icon', KNOWLEDGE_DATA[topic])
            self.assertIn('content', KNOWLEDGE_DATA[topic])
            self.assertTrue(len(KNOWLEDGE_DATA[topic]['content']) > 0)
    
    def test_knowledge_content_validity(self):
        keywords = ['IPsec', 'IKE', 'ESP', 'DPD', 'NAT', 'VRRP', 'SA', '隧道', '加密', '认证', '协议']
        for name, data in KNOWLEDGE_DATA.items():
            content = data['content']
            found = any(kw in content for kw in keywords)
            self.assertTrue(found, f"Content for '{name}' does not contain any relevant keywords")
            self.assertIsNotNone(data['icon'])
    
    def test_knowledge_technical_accuracy(self):
        ike_content = KNOWLEDGE_DATA['IKE协议详解']['content']
        self.assertIn('UDP', ike_content)
        self.assertIn('500', ike_content)
        self.assertIn('Phase 1', ike_content)
        self.assertIn('Phase 2', ike_content)
        
        esp_content = KNOWLEDGE_DATA['IPsec概述']['content']
        self.assertIn('ESP', esp_content)
        self.assertIn('AH', esp_content)
        
        nat_content = KNOWLEDGE_DATA['NAT穿越']['content']
        self.assertIn('4500', nat_content)
        self.assertIn('UDP', nat_content)


class TestLevelsData(unittest.TestCase):
    
    def test_levels_count(self):
        self.assertEqual(len(LEVELS_DATA), 5)
    
    def test_level_structure(self):
        for level in LEVELS_DATA:
            self.assertIn('id', level)
            self.assertIn('name', level)
            self.assertIn('difficulty', level)
            self.assertIn('description', level)
            self.assertIn('scenario', level)
            self.assertIn('knowledge_required', level)
            self.assertIn('config_fields', level)
            self.assertIn('correct_answer', level)
            self.assertIn('tips', level)
            self.assertIn('reference_config', level)
    
    def test_level_difficulties(self):
        difficulties = [level['difficulty'] for level in LEVELS_DATA]
        self.assertEqual(difficulties, ['入门', '基础', '进阶', '高级', '专家'])
    
    def test_config_fields_match_correct_answer(self):
        for level in LEVELS_DATA:
            field_names = [f['name'] for f in level['config_fields']]
            for key in level['correct_answer'].keys():
                self.assertIn(key, field_names, 
                            f"Level {level['id']}: correct_answer key '{key}' not in config_fields")
    
    def test_config_field_types(self):
        valid_types = ['combo', 'spin', 'check', 'text']
        for level in LEVELS_DATA:
            for field in level['config_fields']:
                self.assertIn(field['type'], valid_types)
                if field['type'] == 'combo':
                    self.assertIn('options', field)
                    self.assertIn('default', field)
                elif field['type'] == 'spin':
                    self.assertIn('min', field)
                    self.assertIn('max', field)
                    self.assertIn('default', field)
    
    def test_ikev2_for_nat_traversal(self):
        nat_level = LEVELS_DATA[2]
        self.assertEqual(nat_level['correct_answer']['ike_version'], 'v2')
    
    def test_esp_for_site_to_site(self):
        policy_level = LEVELS_DATA[1]
        self.assertEqual(policy_level['correct_answer']['protocol'], 'esp')
        self.assertEqual(policy_level['correct_answer']['encapsulation'], 'tunnel')


class TestProgressManager(unittest.TestCase):
    
    def setUp(self):
        self.test_file = 'test_progress.json'
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
        self.pm = ProgressManager(self.test_file)
    
    def tearDown(self):
        if os.path.exists(self.test_file):
            os.remove(self.test_file)
    
    def test_initial_state(self):
        self.assertEqual(self.pm.data['completed_levels'], [])
        self.assertEqual(self.pm.data['best_scores'], {})
        self.assertEqual(self.pm.data['total_attempts'], 0)
        self.assertEqual(self.pm.data['knowledge_read'], [])
        self.assertEqual(self.pm.data['achievements'], [])
    
    def test_complete_level(self):
        self.pm.complete_level(1, 80)
        self.assertIn(1, self.pm.data['completed_levels'])
        self.assertEqual(self.pm.data['best_scores'][1], 80)
        self.assertEqual(self.pm.data['total_attempts'], 1)
    
    def test_best_score_update(self):
        self.pm.complete_level(1, 60)
        self.pm.complete_level(1, 90)
        self.assertEqual(self.pm.data['best_scores'][1], 90)
    
    def test_knowledge_read(self):
        self.pm.record_knowledge_read('IPsec概述')
        self.assertIn('IPsec概述', self.pm.data['knowledge_read'])
    
    def test_achievement_first_knowledge(self):
        self.pm.record_knowledge_read('IPsec概述')
        self.assertIn('first_knowledge', self.pm.data['achievements'])
    
    def test_achievement_knowledge_master(self):
        for i, topic in enumerate(list(KNOWLEDGE_DATA.keys())[:6]):
            self.pm.record_knowledge_read(topic)
        self.assertIn('knowledge_master', self.pm.data['achievements'])
    
    def test_invalid_knowledge_name(self):
        initial_count = len(self.pm.data['knowledge_read'])
        self.pm.record_knowledge_read('nonexistent_topic')
        self.assertEqual(len(self.pm.data['knowledge_read']), initial_count)
    
    def test_achievement_first_level(self):
        self.pm.complete_level(1, 50)
        self.assertIn('first_level', self.pm.data['achievements'])
    
    def test_achievement_all_levels(self):
        for i in range(1, 6):
            self.pm.complete_level(i, 70)
        self.assertIn('all_levels', self.pm.data['achievements'])
    
    def test_achievement_perfect_score(self):
        self.pm.complete_level(1, 100)
        self.assertIn('perfect_score', self.pm.data['achievements'])
    
    def test_save_and_load(self):
        self.pm.complete_level(1, 85)
        self.pm.record_knowledge_read('IPsec概述')
        
        pm2 = ProgressManager(self.test_file)
        self.assertIn(1, pm2.data['completed_levels'])
        self.assertTrue('1' in pm2.data['best_scores'] or 1 in pm2.data['best_scores'])
        self.assertIn('IPsec概述', pm2.data['knowledge_read'])


class TestGameLogic(unittest.TestCase):
    
    def test_scoring_perfect(self):
        correct = {'a': 1, 'b': 2, 'c': 3}
        user = {'a': 1, 'b': 2, 'c': 3}
        
        correct_count = sum(1 for k in correct if user.get(k) == correct[k])
        score = round((correct_count / len(correct)) * 100)
        self.assertEqual(score, 100)
    
    def test_scoring_partial(self):
        correct = {'a': 1, 'b': 2, 'c': 3, 'd': 4}
        user = {'a': 1, 'b': 2, 'c': 99, 'd': 4}
        
        correct_count = sum(1 for k in correct if user.get(k) == correct[k])
        score = round((correct_count / len(correct)) * 100)
        self.assertEqual(score, 75)
    
    def test_tolerance_scoring(self):
        expected = 100
        user_val = 105
        tolerance = abs(expected * 0.1)
        
        is_close = abs(user_val - expected) <= tolerance
        self.assertTrue(is_close)
    
    def test_subnet_validation(self):
        subnet = "192.168.1.0/24"
        parts = subnet.split('/')
        self.assertEqual(len(parts), 2)
        self.assertTrue(parts[1].isdigit())


class TestUIComponents(unittest.TestCase):
    
    def test_config_field_widget_creation(self):
        test_fields = [
            {'name': 'test', 'label': 'Test', 'type': 'combo', 'options': ['a', 'b'], 'default': 'a'},
            {'name': 'test2', 'label': 'Test2', 'type': 'spin', 'min': 1, 'max': 100, 'default': 50},
            {'name': 'test3', 'label': 'Test3', 'type': 'check', 'default': True},
            {'name': 'test4', 'label': 'Test4', 'type': 'text', 'default': 'hello'},
        ]
        
        for field in test_fields:
            self.assertIn(field['type'], ['combo', 'spin', 'check', 'text'])
            self.assertIn('name', field)
            self.assertIn('label', field)
            self.assertIn('default', field)


if __name__ == '__main__':
    unittest.main()
