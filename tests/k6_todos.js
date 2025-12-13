import http from 'k6/http';
import { check, sleep } from 'k6';

export let options = {
  vus: 5,           
  duration: '20s',  
};

export default function () {
  
  let res = http.get('http://app.stage.svc.cluster.local/');
  check(res, {
    'GET / status is 200': (r) => r.status === 200,
  });

  
  let create = http.post('http://app.stage.svc.cluster.local/',
    JSON.stringify({ title: 'k6 test' }),
    { headers: { 'Content-Type': 'application/json' } }
  );
  check(create, {
    'POST / status is 200': (r) => r.status === 200,
  });

  
  let todoId = create.json('id');
  if (todoId) {
    let toggle = http.put(`http://app.stage.svc.cluster.local/${todoId}/toggle`);
    check(toggle, {
      'PUT /{id}/toggle status is 200': (r) => r.status === 200,
    });
  }

  
  if (todoId) {
    let del = http.del(`http://app.stage.svc.cluster.local/${todoId}`);
    check(del, {
      'DELETE /{id} status is 200': (r) => r.status === 200,
    });
  }

  sleep(1);
}
