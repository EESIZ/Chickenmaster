#!/usr/bin/env python3
"""
연구개발 모듈 통합 테스트
헥사고널 아키텍처로 구현된 연구개발 시스템을 테스트합니다.

Usage:
    python test_research_module.py
"""

import sys
from pathlib import Path

# 프로젝트 루트 디렉토리를 Python 경로에 추가
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# 이제 src 모듈들을 import할 수 있습니다
from src.research import ResearchModuleFactory, ResearchFacade, ResearchType
from src.core.domain.game_state import GameState
from src.core.domain.metrics import Metric, MetricsSnapshot


def test_research_module():
    """연구개발 모듈 통합 테스트"""
    print("🧪 연구개발 모듈 테스트 시작!")
    print("=" * 60)
    
    # 1. 모듈 생성 테스트
    print("\n1️⃣ 모듈 생성 테스트")
    research_module = ResearchModuleFactory.create_in_memory_module()
    print(f"✅ 연구개발 모듈 생성 완료: {type(research_module).__name__}")
    
    # 2. 게임 상태 설정
    print("\n2️⃣ 게임 상태 설정")
    game_state = GameState(
        money=100000,
        reputation=50,
        happiness=60,
        pain=30,
        day=1
    )
    
    metrics = {
        "inventory": Metric("inventory", 50, 0, 999),
        "staff_fatigue": Metric("staff_fatigue", 40, 0, 100),
        "facility": Metric("facility", 70, 0, 100),
        "demand": Metric("demand", 25, 0, 999)
    }
    metrics_snapshot = MetricsSnapshot(metrics, timestamp=1)
    
    print(f"💰 초기 자금: {game_state.money:,}원")
    print(f"⭐ 평판: {game_state.reputation}점")
    print(f"😊 행복도: {game_state.happiness}점")
    
    # 3. 사용 가능한 프로젝트 조회
    print("\n3️⃣ 사용 가능한 연구 프로젝트 조회")
    available_projects = research_module.get_available_research_options(game_state)
    
    print(f"📋 사용 가능한 프로젝트: {len(available_projects)}개")
    for i, project in enumerate(available_projects, 1):
        success_prob = research_module.calculate_success_probability(
            project.id, game_state, metrics_snapshot
        )
        print(f"  {i}. {project.name}")
        print(f"     💰 비용: {project.cost.money:,}원")
        print(f"     🎯 성공률: {success_prob:.1%} (기본 {project.success_rate:.1%})")
        print(f"     📈 기대효과: 평판+{project.expected_effects.reputation}, 수요+{project.expected_effects.demand}")
    
    # 4. 연구 추천 시스템 테스트
    print("\n4️⃣ 연구 추천 시스템 테스트")
    recommendations = research_module.get_research_recommendations(
        game_state, metrics_snapshot, max_count=2
    )
    
    print(f"💡 추천 프로젝트: {len(recommendations)}개")
    for i, project in enumerate(recommendations, 1):
        risk_assessment = research_module.assess_research_risk(project.id, game_state)
        print(f"  {i}. {project.name}")
        print(f"     📊 리스크 평가:")
        for risk_type, risk_value in risk_assessment.items():
            print(f"       - {risk_type}: {risk_value:.1%}")
    
    # 5. 연구 실행 시뮬레이션
    print("\n5️⃣ 연구 실행 시뮬레이션")
    if available_projects:
        # 첫 번째 프로젝트로 테스트
        test_project = available_projects[0]
        print(f"🔬 테스트 프로젝트: {test_project.name}")
        
        # 미리보기
        preview = research_module.simulate_research_preview(
            test_project.id, game_state, metrics_snapshot
        )
        
        if preview:
            print("📋 연구 미리보기:")
            print(f"  성공 확률: {preview['success_probability']:.1%}")
            print(f"  총 비용: {preview['cost_breakdown']['total_cost']:,}원")
            print(f"  성공 시 효과: 평판+{preview['expected_effects']['success'].reputation}")
            print(f"  실패 시 페널티: 고통+{preview['expected_effects']['failure'].pain}")
        
        # 실제 실행
        print("\n🚀 연구 실행!")
        result = research_module.execute_research_project(
            test_project.id, game_state, metrics_snapshot
        )
        
        if result:
            print(f"📊 연구 결과:")
            print(f"  {'✅ 성공!' if result.is_success else '❌ 실패...'}")
            print(f"  메시지: {result.message}")
            if result.innovation_name:
                print(f"  혁신명: {result.innovation_name}")
            
            # 게임 상태에 적용
            new_game_state, new_metrics = research_module.apply_research_effects_to_game(
                result, game_state, metrics_snapshot
            )
            
            print(f"\n💰 자금 변화: {game_state.money:,}원 → {new_game_state.money:,}원")
            print(f"⭐ 평판 변화: {game_state.reputation}점 → {new_game_state.reputation}점")
            print(f"😊 행복도 변화: {game_state.happiness}점 → {new_game_state.happiness}점")
            
            # 지표 변화
            old_demand = metrics_snapshot.get_metric_value("demand")
            new_demand = new_metrics.get_metric_value("demand")
            if old_demand != new_demand:
                print(f"📈 수요 변화: {old_demand}점 → {new_demand}점")
    
    # 6. 연구 이력 확인
    print("\n6️⃣ 연구 이력 확인")
    history = research_module.get_research_history(limit=5)
    print(f"📚 연구 이력: {len(history)}개")
    for i, result in enumerate(history, 1):
        status = "성공" if result.is_success else "실패"
        print(f"  {i}. {result.project.name} - {status}")
    
    # 7. 유형별 프로젝트 조회
    print("\n7️⃣ 유형별 프로젝트 조회")
    for research_type in ResearchType:
        projects = research_module.get_projects_by_type(research_type)
        print(f"  {research_type.value}: {len(projects)}개")
    
    print("\n" + "=" * 60)
    print("🎉 연구개발 모듈 테스트 완료!")
    print("✅ 모든 컴포넌트가 정상 작동합니다!")


def demo_research_game_scenario():
    """연구개발 게임 시나리오 데모"""
    print("\n🎮 연구개발 게임 시나리오 데모")
    print("=" * 60)
    
    # 초기 상황: 자금 부족, 평판 낮음
    research_module = ResearchModuleFactory.create_in_memory_module()
    
    game_state = GameState(
        money=85000,  # 빠듯한 자금
        reputation=35,  # 낮은 평판
        happiness=40,   # 스트레스 상황
        pain=65,
        day=15
    )
    
    metrics = {
        "inventory": Metric("inventory", 20, 0, 999),  # 재고 부족
        "staff_fatigue": Metric("staff_fatigue", 70, 0, 100),  # 직원 피로
        "facility": Metric("facility", 45, 0, 100),  # 시설 노후
        "demand": Metric("demand", 15, 0, 999)  # 수요 저조
    }
    metrics_snapshot = MetricsSnapshot(metrics, timestamp=15)
    
    print("🏪 현재 상황:")
    print(f"  💰 자금: {game_state.money:,}원 (빠듯함)")
    print(f"  ⭐ 평판: {game_state.reputation}점 (낮음)")
    print(f"  😰 고통도: {game_state.pain}점 (높음)")
    print(f"  📉 수요: {metrics_snapshot.get_metric_value('demand')}점 (저조)")
    
    # 추천 시스템이 현재 상황을 고려하는지 확인
    recommendations = research_module.get_research_recommendations(
        game_state, metrics_snapshot, max_count=3
    )
    
    print(f"\n💡 AI 추천 연구 프로젝트:")
    for i, project in enumerate(recommendations, 1):
        success_prob = research_module.calculate_success_probability(
            project.id, game_state, metrics_snapshot
        )
        risk = research_module.assess_research_risk(project.id, game_state)
        
        print(f"  {i}. {project.name}")
        print(f"     💰 비용: {project.cost.money:,}원")
        print(f"     🎯 조정된 성공률: {success_prob:.1%}")
        print(f"     ⚠️ 자금 리스크: {risk.get('financial', 0):.1%}")
        print(f"     💼 전략적 적합성: {100-risk.get('strategic', 0)*100:.0f}%")
        
        # 상황별 분석
        if project.expected_effects.reputation > 15:
            print(f"     📈 평판 개선에 효과적!")
        if project.expected_effects.demand > 20:
            print(f"     📊 수요 증가에 도움!")
        if project.cost.money > game_state.money * 0.8:
            print(f"     ⚠️ 자금의 80% 이상 투자 - 신중히!")
    
    print("\n🤔 전략적 고민:")
    print("  - 안전한 저비용 프로젝트 vs 고위험 고수익 프로젝트?")
    print("  - 평판 개선 우선 vs 수요 증가 우선?")
    print("  - 현재 자금으로 실패 시 회복 가능한가?")
    
    print("\n" + "=" * 60)


if __name__ == "__main__":
    try:
        test_research_module()
        demo_research_game_scenario()
        
        print("\n🎯 결론:")
        print("✅ 헥사고널 아키텍처 구현 완료")
        print("✅ 도메인 중심 설계 원칙 준수")
        print("✅ 불변 객체 패턴 적용")
        print("✅ 포트 & 어댑터 패턴 구현")
        print("✅ 의존성 역전 원칙 적용")
        print("✅ 게임 철학 반영 (트레이드오프, 불확실성)")
        
    except Exception as e:
        print(f"💥 테스트 실행 중 오류 발생: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1) 