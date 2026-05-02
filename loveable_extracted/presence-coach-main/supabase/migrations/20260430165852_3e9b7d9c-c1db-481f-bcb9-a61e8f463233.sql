-- Create private bucket for CV uploads
insert into storage.buckets (id, name, public)
values ('cvs', 'cvs', false)
on conflict (id) do nothing;

-- RLS policies: users can only access their own folder
create policy "Users can view their own CVs"
on storage.objects for select
to authenticated
using (bucket_id = 'cvs' and auth.uid()::text = (storage.foldername(name))[1]);

create policy "Users can upload their own CVs"
on storage.objects for insert
to authenticated
with check (bucket_id = 'cvs' and auth.uid()::text = (storage.foldername(name))[1]);

create policy "Users can update their own CVs"
on storage.objects for update
to authenticated
using (bucket_id = 'cvs' and auth.uid()::text = (storage.foldername(name))[1]);

create policy "Users can delete their own CVs"
on storage.objects for delete
to authenticated
using (bucket_id = 'cvs' and auth.uid()::text = (storage.foldername(name))[1]);