-- ARTEX 0.3.15-global.1의 새 데이터베이스에 남아 있는 중국어 기본 Agent 이름만 한글화한다.
-- 사용자가 이미 바꾼 이름은 덮어쓰지 않는다.
UPDATE agents SET name = '목표 분해' WHERE key = 'goals' AND name = '目标拆解';
UPDATE agents SET name = '계획 수립' WHERE key = 'planner' AND name = '规划';
UPDATE agents SET name = '메인 에이전트' WHERE key = 'mainagent' AND name = '主';
UPDATE agents SET name = '실행 작업자' WHERE key = 'worker' AND name = '执行';
UPDATE agents SET name = '모의해킹' WHERE key = 'pentest' AND name = '渗透测试';
UPDATE agents SET name = '취약점 재검증' WHERE key = 'retester' AND name = '漏洞复测';

-- Worker는 현재 Task에 연결된 list_assets만 사용한다. 회사 전체 목록을 열거해 다른 기관을
-- 추측하지 못하도록 list_companies 노출에서 worker를 제거한다.
UPDATE tools
   SET agents = COALESCE(
     (SELECT jsonb_agg(value) FROM jsonb_array_elements(agents) value WHERE value <> '"worker"'::jsonb),
     '[]'::jsonb
   )
 WHERE key = 'list_companies';

-- 강의용 범위 연결 보조 장치.
-- 사용자가 기업 화면에 직접 입력한 명시적 HTTP(S) URL을, 해당 기업이 Task에 선택되는 순간
-- 그 Task의 시작 service 자산으로 연결한다. 네트워크 탐색이나 범위 확장은 하지 않는다.
-- ARTEX 0.3.15에서 company scope만 선택하면 Worker의 list_assets가 0건으로 보일 수 있어,
-- LLM이 다른 회사 URL을 추측하지 않도록 정확한 입력 URL만 연결하는 안전장치다.
CREATE OR REPLACE FUNCTION course_link_company_scope_service()
RETURNS trigger
LANGUAGE plpgsql
AS $$
DECLARE
  scope_row record;
  service_port integer;
BEGIN
  IF NEW.kind <> 'company' OR NEW.company_id IS NULL THEN
    RETURN NEW;
  END IF;

  FOR scope_row IN
    SELECT domain, raw
      FROM company_scope
     WHERE company_id = NEW.company_id
       AND kind = 'domain'
       AND raw ~ '^https?://'
  LOOP
    service_port := COALESCE(
      NULLIF(substring(scope_row.raw from '://[^/:]+:([0-9]+)'), '')::integer,
      CASE WHEN scope_row.raw ~ '^https://' THEN 443 ELSE 80 END
    );

    INSERT INTO assets (
      type, company_id, company_source, task_ids, domain, port, url,
      service_type, service_name, extra
    ) VALUES (
      'service', NEW.company_id, 'explicit', ARRAY[NEW.task_id], scope_row.domain,
      service_port, scope_row.raw, 'http',
      CASE WHEN scope_row.raw ~ '^https://' THEN 'HTTPS' ELSE 'HTTP' END,
      jsonb_build_object('course_scope_bridge', true)
    )
    ON CONFLICT (url) WHERE type = 'service' AND service_type = 'http'
    DO UPDATE SET
      company_id = EXCLUDED.company_id,
      company_source = 'explicit',
      task_ids = CASE
        WHEN NEW.task_id = ANY(assets.task_ids) THEN assets.task_ids
        ELSE array_append(assets.task_ids, NEW.task_id)
      END,
      last_seen = now();
  END LOOP;

  RETURN NEW;
END;
$$;

DROP TRIGGER IF EXISTS trg_course_link_company_scope_service ON task_scope;
CREATE TRIGGER trg_course_link_company_scope_service
AFTER INSERT ON task_scope
FOR EACH ROW
EXECUTE FUNCTION course_link_company_scope_service();
