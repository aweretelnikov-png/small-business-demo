# Backup и проверка восстановления CRM

## Создать полный backup

Из каталога `crm-leads`:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\backup.ps1
```

Backup создаётся в `backups/<timestamp>/` и включает:

- `crm_demo.dump`;
- `twenty.dump`;
- `twenty-local-storage/`;
- `metabase-data/`;
- `manifest.txt`;
- `checksums.sha256`.

Twenty и Metabase кратко останавливаются для согласованного копирования и запускаются обратно.

## Проверить восстановление crm_demo

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\test_restore_crm.ps1
```

Используется временная база `crm_restore_test`, которая удаляется автоматически.

## Проверить восстановление Twenty

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\test_restore_twenty.ps1
```

Используется временная база `twenty_restore_test`, которая удаляется автоматически.

## Проверить восстановление Metabase

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\start_metabase_restore_test.ps1
```

Изолированная копия доступна на <http://localhost:3005>. После проверки:

```cmd
powershell -NoProfile -ExecutionPolicy Bypass -File scripts\stop_metabase_restore_test.ps1
```

## Секреты

Backup может содержать персональные данные и игнорируется Git.

Локальные `.env` не включаются. Их нужно хранить отдельно в защищённом хранилище. Особенно важен `crm-leads/twenty/.env`: потеря `ENCRYPTION_KEY` делает зашифрованные секреты Twenty недоступными.

Не публикуйте backup, `.env`, API-ключи, токены и реальные персональные данные.
